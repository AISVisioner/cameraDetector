from django.utils import timezone
import datetime

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from lookup.api.serializers import VisitorSerializer
from lookup.models import Visitor
from lookup.api.visitorsUtils import initializeVisitors

import face_recognition
import numpy as np

class LookupViewSet(viewsets.ModelViewSet):
    """Provide CRUD + L functionality for Lookup."""

    queryset = Visitor.objects.all().order_by("-created_at")
    serializer_class = VisitorSerializer
    authentication_classes = [TokenAuthentication] # Authenticate access to API by issueing a token
    permission_classes = [IsAuthenticated] # Login required
    lookup_field = "id"
    _visitors_data = initializeVisitors(queryset, serializer_class) # { uuid : encoding, ....}
    _visitors = _visitors_data.getVisitors()
    __LAPSE = datetime.timedelta(seconds=40) # waiting time for a duplicate user

    def list(self, request):
        """Use this overridden method to list all the visitors in admin page."""
        # self._visitors_data.updateSerializer()
        serializer = self._visitors_data.getSerializer()
        return Response(serializer.data)

    def create(self, request):
        """Add request as a lookup instance after verication"""
        self._visitors_data.updateQueryset() # to be deleted
        self._visitors_data.updateSerializer(save=False) # to be deleted
        self._visitors_data.updateVisitors() # to be deleted
        self._visitors = self._visitors_data.getVisitors()
        request.data.setlist('encoding', list(map(float, request.data.getlist('encoding')))) # convert encoding type from str to float(for calculation)
        user_matched = face_recognition.compare_faces(list(self._visitors.values()), np.array(request.data.getlist('encoding'))) # calculate similarity between a requested user and all the visitors in DB(necessity of improvement in efficiency of calculation(redundant calculation?))
        print('matched?', user_matched) # [True/False] -> If True is in the list, there's data of a current visitor

        for i, user_matched in enumerate(user_matched): # Check if the same visitor exists
            if user_matched: # if there's the same user
                user_id_matched = list(self._visitors.keys())[i] # get the visitor's uuid
                instance = self._visitors_data.getQueryset().get(pk=user_id_matched) # find an instance of the visitor
                if timezone.now() - instance.recent_access_at <= self.__LAPSE: # if the same user continuously tries to check in
                    return Response(None, status=status.HTTP_304_NOT_MODIFIED)

                data = {'visits_count': instance.visits_count+1, 'created_at': timezone.now()} # create a data dictionary for partial_update(note timezone.now() isn't passed to validated_data(some internal error?))
                self._visitors_data.updateSerializer(instance=instance, data=data, partial=True) # update not visitors, but a serialiser
                # self._visitors_data.updateSerializer(instance=instance, data=data, partial=True, many=False) 
                serializer = self._visitors_data.getSerializer()

                print(f'matched no.{i} {list(self._visitors)[i]}')

                return Response(serializer.data, status=status.HTTP_200_OK)

        # if the requested user isn't registerd
        print(f'new user {request.data["id"]}')

        # create a serializer with the requested data
        self._visitors_data.updateSerializer(data=request.data)

        # update the fields of viewset class everytime a new visitor is registered
        self._visitors_data.updateVisitors(init=True)
        serializer = self._visitors_data.getSerializer()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass