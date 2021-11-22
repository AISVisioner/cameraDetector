from rest_framework import serializers
from django.utils import timezone

from lookup.models import Visitor

class VisitorSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(format="hex")
    # name = serializers.CharField()
    encoding = serializers.ListField(child=serializers.FloatField())
    # photo = serializers.ImageField(required=False)
    # visits_count = serializers.IntegerField()
    recent_access_at = serializers.SerializerMethodField() # use the method below
    created_at = serializers.SerializerMethodField() # use the method below
    updated_at = serializers.SerializerMethodField() # use the method below
    
    class Meta:
        model = Visitor
        fields = ['id', 'name', 'encoding', 'photo', 'visits_count', 'created_at', 'updated_at', 'recent_access_at']
        exclude = []

    def create(self, validated_data):
        # create an object which can be saved as a new instance in Visitor Table.
        visitor = Visitor.objects.create(**validated_data)
        visitor.save() # save the object as a record in DB
        return visitor

    def update(self, instance, validated_data):
        # if the update is for a visitor
        if instance.visits_count + 1 == validated_data['visits_count']:
            # update two fields below
            instance.visits_count = validated_data['visits_count']
            instance.recent_access_at = timezone.now()
            instance.save() # save the instance to database
            return instance

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y-%m-%d_%H:%M:%S")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y-%m-%d_%H:%M:%S")

    def get_recent_access_at(self, instance):
        return instance.recent_access_at.strftime("%Y-%m-%d_%H:%M:%S")