from django.utils import timezone
import datetime

from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
# from lookup.api.permissions import DeleteForAdminOrSafeOnly
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from lookup.models import Visitor
from lookup.api.serializers import VisitorSerializer

from lookup.api.visitorsUtils import initializeVisitors

import face_recognition
import numpy as np

class LookupViewSet(viewsets.ModelViewSet):
    """Provide CRUD + L functionality for Lookup."""
    # authentication_classes = [TokenAuthentication] # Authenticate access to API by issueing a token
    queryset = Visitor.objects.all().order_by("-created_at")
    serializer_class = VisitorSerializer
    permission_classes = [IsAdminUser] # Allows access only to authenticated users.
    lookup_field = "id" # pk
    _visitors_data = initializeVisitors() # instantiate VisitorsData class(a singleton class)
    _visitors = _visitors_data.getVisitors() # initialize the visitors field(type: dict): {uuid: face_encodings}
    __LAPSE = datetime.timedelta(seconds=40) # waiting time for a duplicate user
    __TOLERANCE = 0.4 # threshold for face_distance

    def list(self, request):
        """Use this overridden method to list all the visitors in admin page."""
        self._visitors_data.updateQueryset() # use this to update the queryset everytime any instance is deleted from the DB.
        self._visitors_data.updateSerializer(save=False) # update the serializer with the queryset above
        serializer = self._visitors_data.getSerializer() # get the serializer 
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Add request as a lookup instance after verication"""
        self._visitors_data.updateQueryset() # use this to update the queryset everytime any instance is deleted from the DB.
        self._visitors_data.updateSerializer(save=False) # update the serializer with the queryset above
        self._visitors_data.updateVisitors() # update the _visitors field with the updated serializer above
        self._visitors = self._visitors_data.getVisitors()
        request.data.setlist('encoding', list(map(float, request.data.getlist('encoding')))) # convert encoding type from str to float(for calculation)

        if self._visitors: # If there're any existing visitors -> if false, the visitor is recorded as a new visitor automatically
            face_distance_arr = face_recognition.face_distance(list(self._visitors.values()), np.array(request.data.getlist('encoding'))) # get a np.array of all the distances between each visitor in db and the current visitor.
            min_visitor_distance = face_distance_arr.min() # minimum value of face_distance_arr
            print('min_visitor_distance:', min_visitor_distance)
            min_visitor_index = face_distance_arr.argmin() # minumum index of face_distance_arr
            print('min_visitor_index:', min_visitor_index)
            if min_visitor_distance <= self.__TOLERANCE: # if the minimum value of face_distance_arr is smaller than or equal to the tolerance threshold
                user_id_matched = list(self._visitors.keys())[min_visitor_index] # get the visitor's uuid
                instance = self._visitors_data.getQueryset().get(pk=user_id_matched) # find an instance of the visitor
                if timezone.now() - instance.recent_access_at <= self.__LAPSE: # if the same user continuously tries to check in
                    return Response(None, status=status.HTTP_304_NOT_MODIFIED)

                data = {'visits_count': instance.visits_count+1, 'created_at': timezone.now()} # create a data dictionary for partial_update(note timezone.now() isn't passed to validated_data(some internal error?))
                self._visitors_data.updateSerializer(instance=instance, data=data, partial=True) # update not visitors, but a serialiser
                serializer = self._visitors_data.getSerializer()

                print(f'matched no.{min_visitor_index} {list(self._visitors)[min_visitor_index]}')
                
                return Response(serializer.data, status=status.HTTP_200_OK)

        # if the requested user isn't registerd
        print(f'new user {request.data["id"]}') 

        # update the fields of visitors_data object everytime a new visitor is registered
        self._visitors_data.updateSerializer(data=request.data) # update the serializer field with the requested data
        serializer = self._visitors_data.getSerializer() # get the updated serializer

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, id=None):
        self._visitors_data.updateQueryset()
        self._visitors_data.updateSerializer(save=False)

        instance = self._visitors_data.getQueryset().get(pk=id)
        data = {'name': request.data['name'], 'visits_count': instance.visits_count, 'updated_at': timezone.now()}
        self._visitors_data.updateSerializer(instance=instance, data=data, partial=True)
        print(f"updated a user's name of id-{instance.id} to {request.data['name']}")
        return Response({"status": "Success"}, status=status.HTTP_206_PARTIAL_CONTENT)
        
    def destroy(self, request, id=None):
        self._visitors_data.updateQueryset()
        self._visitors_data.updateSerializer(save=False)

        instance = self._visitors_data.getQueryset().get(pk=id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()