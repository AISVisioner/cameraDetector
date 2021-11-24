"""
a module for creating a singleton class of visitors data.
"""

from lookup.models import Visitor
from lookup.api.serializers import VisitorSerializer

class Singleton(type):
    """
    a singleton class. use this as a metaclass to create a class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class VisitorsData(metaclass=Singleton): # use Singleton Class as a metaclass
    """
    visitors data class 
    """
    _visitors = {} # {uuid: face_encoding}
    _queryset = None # a queryset to access data in DB
    _serializer_class = None # a serializer class to create a serializer object
    _serializer = None # a serializer to create a json object from a model class

    def __init__(self):
        self._queryset = Visitor.objects.all().order_by("-created_at")
        self._serializer_class = VisitorSerializer

    def updateQueryset(self):
        self._queryset = Visitor.objects.all().order_by("-created_at") # fetch all the data in DB in reverse order of created_at

    def updateSerializer(self, instance=None, data=None, partial=False, save=True): # save paramter: whether the serializer saves the data or not.
        if save:
            self._serializer = self._serializer_class(instance=instance, data=data, partial=partial) # create a serializer for a partial update
            self._serializer.is_valid(raise_exception=True) # check the consistency of the serializer
            self._serializer.save() # save the serializer object into DB
        else:
            self._serializer = self._serializer_class(self._queryset, many=True) # all the visitors in DB

    def updateVisitors(self): 
        self._visitors = dict(zip([data['id'] for data in self._serializer.data],\
            [data['encoding'] for data in self._serializer.data])) # create a dictionary {uuid: encoding} of all the visitors

    def getQueryset(self):
        return self._queryset

    def getSerializer(self):
        return self._serializer

    def getSerializerClass(self):
        return self._serializer_class

    def getVisitors(self):
        return self._visitors

def initializeVisitors():
    visitors_data = VisitorsData()
    visitors_data.updateSerializer(save=False)
    return visitors_data