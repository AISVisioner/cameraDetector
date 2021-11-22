from lookup.models import Visitor

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class VisitorsData(metaclass=Singleton):
    _visitors = {}
    _queryset = None
    _serializer_class = None
    _serializer = None

    def __init__(self, queryset, serializer_class):
        self._queryset = queryset
        self._serializer_class = serializer_class

    def updateQueryset(self):
        self._queryset = Visitor.objects.all().order_by("-created_at")

    def updateSerializer(self, instance=None, data=None, partial=False, save=True):
        if save:
            self._serializer = self._serializer_class(instance=instance, data=data, partial=partial) # create a serializer for a partial update
            self._serializer.is_valid(raise_exception=True) # check the consistency of the serializer
            self._serializer.save() # save the serializer object into DB
        else:
            self._serializer = self._serializer_class(self._queryset, many=True) # all the visitors in DB

    def updateVisitors(self, init=False):
        if not init:
            self._visitors = dict(zip([data['id'] for data in self._serializer.data],\
                [data['encoding'] for data in self._serializer.data])) # create a dictionary {uuid: encoding} of all the visitors
        else:
            self._visitors = dict([(self._serializer.data['id'], self._serializer.data['encoding'])])

    def getQueryset(self):
        return self._queryset

    def getSerializer(self):
        return self._serializer

    def getSerializerClass(self):
        return self._serializer_class

    def getVisitors(self):
        return self._visitors

def initializeVisitors(queryset, serializer_class):
    visitors_data = VisitorsData(queryset, serializer_class)
    visitors_data.updateSerializer(save=False)
    return visitors_data