""" Production Settings """

# import os
# import dj_database_url
from .base import *

############
# DATABASE #
############
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL')
#     )
# }


############
# SECURITY #
############

DEBUG = True # bool(os.getenv('DJANGO_DEBUG', ''))

# Set to your Domain here (eg. 'yourwebsite.com')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    },
}