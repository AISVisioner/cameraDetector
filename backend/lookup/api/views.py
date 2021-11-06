from django.utils import timezone
import datetime

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from lookup.api.serializers import UserSerializer
from lookup.models import Visitor

import face_recognition
import numpy as np

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
        queryset = Visitor.objects.all().order_by("-created_at")
        serializer = self.serializer_class(queryset, many=True) # all the visitors in DB
        users = dict(zip([data['id'] for data in serializer.data], [data['encoding'] for data in serializer.data])) # create a dictionary {uuid: encoding} of all the visitors

        request.data.setlist('encoding', list(map(float, request.data.getlist('encoding')))) # convert encoding type from str to float(for calculation)
        user_matched = face_recognition.compare_faces(list(users.values()), np.array(request.data.getlist('encoding'))) # calculate similarity between a requested user and all the visitors in DB(necessity of improvement in efficiency of calculation(redundant calculation?))
        print('matched?', user_matched) # [True/False] -> If True is in the list, there's data of a current visitor

        for i, user_matched in enumerate(user_matched): # Check if the same visitor exists
            if user_matched: # if there's the same user
                user_id_matched = list(users.keys())[i] # get the visitor's uuid
                instance = self.queryset.get(pk=user_id_matched) # find an instance of the visitor
                if timezone.now() - instance.recent_access_at <= LAPSE: # if the same user continuously tries to check in
                    return Response(None, status=status.HTTP_304_NOT_MODIFIED)

                data = {'visits_count': instance.visits_count+1, 'created_at': timezone.now()} # create a data dictionary for partial_update(note timezone.now() isn't passed to validated_data(some internal error?))
                serializer = self.serializer_class(instance, data=data, partial=True) # create a serializer for a partial update
                serializer.is_valid(raise_exception=True) # check the consistency of the serializer
                serializer.save() # save the serializer object into DB

                print(f'matched no.{i} {list(users)[i]}')

                return Response(serializer.data, status=status.HTTP_200_OK)

        # if the requested user isn't registerd
        print(f'new user {request.data["id"]}')

        # create a serializer with the requested data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True) # check the consistency of the serializer
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass