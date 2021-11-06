import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

# class Visitor(models.Model):
class Visitor(models.Model):
    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False) # identifier
    name = models.CharField(blank=False, editable=True, max_length=100) # visitor's name
    encoding = ArrayField(models.FloatField(blank=True, editable=False), blank=True, editable=True) # visitor's face codes
    photo = models.ImageField(blank=True, editable=True, upload_to='') # image file
    visits_count = models.IntegerField(default=1, blank=True, editable=True) # the number of visits
    recent_access_at = models.DateTimeField(default=timezone.now, editable=True) # recent access of a visitor
    created_at = models.DateTimeField(auto_now_add=True, editable=False) # when this instance was created
    updated_at = models.DateTimeField(default=timezone.now, editable=True) # when this instance was updated

    def __str__(self):
        return self.name