from rest_framework import serializers

from lookup.models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex")
    # encoding = serializers.ListField(child=serializers.FloatField(read_only=True))
    photo = serializers.ImageField()
    visits_count = serializers.IntegerField()
    recent_access_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        exclude = []

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y%m%d-%H:%M:%S")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y%m%d-%H:%M:%S")

    def get_recent_access_at(self, instance):
        return instance.recent_access_at.strftime("%Y%m%d-%H:%M:%S")