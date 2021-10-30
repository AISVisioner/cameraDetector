import uuid
# from django.conf import settings
from django.db import models
# from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth.models import AbstractBaseUser

# class Visitor(models.Model):
class Visitor(models.Model):
    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=False, editable=True, max_length=100)
    encoding = ArrayField(models.FloatField(blank=True, editable=False), blank=True, editable=True)
    photo = models.ImageField(blank=True, editable=True, upload_to='')
    visits_count = models.IntegerField(default=1, blank=True, editable=True)
    recent_access_at = models.DateTimeField(auto_now_add=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name