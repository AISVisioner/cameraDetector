from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lookup.api.serializers import UserSerializer
from lookup.models import User

class LookupViewSet(viewsets.ModelViewSet):
    """Provide CRUD + L functionality for Lookup."""

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"