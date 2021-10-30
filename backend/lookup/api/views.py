from django.utils import timezone

import re
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from lookup.api.serializers import UserSerializer
from lookup.models import Visitor

import uuid
import face_recognition
import datetime
import numpy as np
import traceback
import copy
from itertools import chain
import time
import pathlib
import imghdr
from PIL import Image
from io import BytesIO

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class LookupViewSet(viewsets.ModelViewSet):
    """Provide CRUD + L functionality for Lookup."""

    queryset = Visitor.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication] # トークンを発行してAPIへの接続を許可する。
    permission_classes = [IsAuthenticated] # Login required
    lookup_field = "id"

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Add request as a lookup instance after verication"""
        print('pass')
        serializer = self.serializer_class(self.queryset, many=True)
        print('pass2')
        print(serializer)
        users = dict(zip([data['id'] for data in serializer.data], [data['encoding'] for data in serializer.data]))
        print('pass2_1')
        registered = False
        _mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST.setlist('encoding', list(map(float, request.POST.getlist('encoding'))))
        request.POST._mutable = _mutable
        user_matched = face_recognition.compare_faces(list(users.values()), np.array(request.POST.getlist('encoding')))
        print(user_matched)
        print('pass2_2')
        for i, user_matched in enumerate(user_matched):
            print('pass2_3')
            if user_matched:
                print('pass2_3_1')
                user_id_matched = list(users.keys())[i]
                instance = self.queryset.get(pk=user_id_matched)
                data = copy.copy(instance)
                data.visits_count = instance.visits_count + 1
                data.recent_access_at = timezone.now().timestamp()
                print('here', data.visits_count)
                data = to_dict(data)
                print(data)
                _serializer = self.serializer_class(instance, data=data, partial=True)
                _serializer.is_valid(raise_exception=True)
                print(_serializer.errors)
                _serializer.save()
                # cv.putText(frame, f'matched no.{i} {list(users)[i]}', (0,50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                print(f'matched no.{i} {list(users)[i]}')
                registered = True
                return Response(_serializer.data, status=status.HTTP_200_OK)
        # if the requested user isn't registerd
        print('pass2_4')
        if not registered:
            # user_id = str(uuid.uuid4())
            print(f'new user {request.POST["id"]}')
            # with open(request.FILES['photo']) as file:
            #     file.write
            # print('type', type(request.FILES['photo']))
            # data = open(request.FILES['photo'], 'rb')
            # print('type', type(data))
            # print('data', type(data), data)
            # path = default_storage.save(f'tmp/{str(request.FILES["photo"])}', ContentFile(data.read()))
            # time.sleep(3)
            # tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            # tmp_file = os.path.join(os.getcwd(), path)
            # pil_image_obj = Image.open(request.FILES['photo'])
            # new_image_io = BytesIO()
            # pil_image_obj.save(new_image_io, format='JPEG')
            # image_file = InMemoryUploadedFile(new_image_io, None, str(request.FILES['photo']), 'image/jpeg',
            #                       new_image_io.getbuffer().nbytes, None)
            # print('image_file', type(image_file), dir(image_file))
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['visits_count'] = 0
            print('here1')
            # try:
            #     data = ImageFile(request.FILES['photo'].read(), name=str(request.FILES['photo']))
            # except:
            #     data = ContentFile(request.FILES['photo'].read(), name=str(request.FILES['photo']))
            # data = ContentFile(request.FILES['photo'])
            data = ImageFile(open(request.FILES['photo']), 'rb')
            request.POST['photo'] = data
            print('here2')
            request.POST._mutable = _mutable
            print('here3')
            print(request.POST)
            print('here4')
            # print(imghdr.what(request.POST['photo']))
            print('pass3')
            _serializer = self.serializer_class(data=request.POST)
            _serializer.is_valid()
            print(_serializer.errors)
            print(_serializer.validated_data)
            print('pass4')
            obj = Visitor.objects.create(**_serializer.validated_data)
            print('pass5')
            obj.save()
            print('pass6')
            return Response(_serializer.validated_data, status=status.HTTP_201_CREATED)

            # users[user_id] = request.encoding

            # cv.putText(frame, f'new user {user_id}', (0,50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
            

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

    # @action(detail=False, methods=['post'])
    # def check_(self, request, id):
    #     user = User.objects.filter(id=id)
    #     return Response()