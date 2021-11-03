from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from lookup.api.serializers import UserSerializer
from lookup.models import Visitor

import face_recognition
import numpy as np
import copy
from itertools import chain
import datetime

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

def to_dict(instance):
    """ convert queried instance to dictionary format """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class LookupViewSet(viewsets.ModelViewSet):
    """Provide CRUD + L functionality for Lookup."""

    queryset = Visitor.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication] # Authenticate access to API by issueing a token
    permission_classes = [IsAuthenticated] # Login required
    lookup_field = "id"

    def list(self, request):
        """Use this overridden method to list all the visitors in admin page."""
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Add request as a lookup instance after verication"""
        LAPSE = datetime.timedelta(seconds=40) # waiting time for a duplicate user
        serializer = self.serializer_class(self.queryset, many=True) # all the visitors in DB
        users = dict(zip([data['id'] for data in serializer.data], [data['encoding'] for data in serializer.data])) # create a dictionary {uuid: encoding} of all the visitors
        registered = False

        _mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST.setlist('encoding', list(map(float, request.POST.getlist('encoding')))) # convert encoding type from str to float(for calculation)
        request.POST._mutable = _mutable

        user_matched = face_recognition.compare_faces(list(users.values()), np.array(request.POST.getlist('encoding'))) # calculate similarity between a requested user and all the visitors in DB(necessity of improvement in efficiency of calculation(redundant calculation?))
        for i, user_matched in enumerate(user_matched): # Check if the same visitor exists
            if user_matched: # if there's the same user
                user_id_matched = list(users.keys())[i] # get the visitor's uuid
                instance = self.queryset.get(pk=user_id_matched) # find an instance of the visitor
                if timezone.now() - instance.recent_access_at <= LAPSE: # if the same user continuously tries to check in
                    return Response(None, status=status.HTTP_304_NOT_MODIFIED)

                data = copy.copy(instance) # create a copy of the instance
                data.visits_count = instance.visits_count + 1 # increase the number of visits of the visitor by 1
                data = to_dict(data) # convert the data to dictionary type

                _serializer = self.serializer_class(instance, data=data, partial=True) # create a serializer for a partial update
                _serializer.is_valid(raise_exception=True) # check the consistency of the serializer
                _serializer.save() # save the serializer object into DB
                print(f'matched no.{i} {list(users)[i]}')
                registered = True # pre-visited user
                return Response(_serializer.data, status=status.HTTP_200_OK)

        # if the requested user isn't registerd
        if not registered:
            print(f'new user {request.POST["id"]}')

            # initialize the number of visits of the visitor(as 0)
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['visits_count'] = 0

            # convert InMemoryUpdatedFile to the format which can be saved as an image file
            # try:
            #     data = ImageFile(ContentFile(request.FILES['photo'].read(), name=str(request.FILES['photo'])))
            # except:
            #     try:
            #         data = ContentFile(request.FILES['photo'])
            #     except:
            #         data = ImageFile(open(request.FILES['photo']), 'rb')
            data = ContentFile(request.FILES['photo'])

            # append the image file to the requested data dictionary
            request.POST['photo'] = data
            request.POST._mutable = _mutable

            # create a serializer with the requested data
            _serializer = self.serializer_class(data=request.POST)
            _serializer.is_valid(raise_exception=True) # check the consistency of the serializer

            # create an object which can be saved as a new instance in Visitor Table.
            obj = Visitor.objects.create(**_serializer.validated_data)
            obj.save() # save the object as a record in DB
            return Response(_serializer.validated_data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass