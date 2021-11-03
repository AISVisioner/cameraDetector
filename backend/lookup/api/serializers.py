from rest_framework import serializers

from lookup.models import Visitor

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex")
    name = serializers.CharField()
    encoding = serializers.ListField(child=serializers.FloatField())
    photo = serializers.ImageField(required=False)
    visits_count = serializers.IntegerField()
    recent_access_at = serializers.SerializerMethodField() # use the method below
    created_at = serializers.SerializerMethodField() # use the method below
    updated_at = serializers.SerializerMethodField() # use the method below
    
    class Meta:
        model = Visitor
        fields = ['id', 'name', 'encoding', 'photo', 'visits_count', 'created_at', 'updated_at', 'recent_access_at']
        exclude = []

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y-%m-%d_%H:%M:%S")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y-%m-%d_%H:%M:%S")

    def get_recent_access_at(self, instance):
        return instance.recent_access_at.strftime("%Y-%m-%d_%H:%M:%S")