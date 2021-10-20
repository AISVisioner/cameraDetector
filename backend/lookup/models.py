import uuid
# from django.conf import settings
from django.db import models
# from django.utils import timezone
# from django.contrib.postgres.fields import ArrayField

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=False, editable=True, max_length=100)
    # encoding = ArrayField(models.FloatField)
    photo = models.ImageField(blank=True, editable=True)
    visits_count = models.IntegerField(default=0, blank=False, editable=True)
    recent_access_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.name