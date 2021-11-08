#!/bin/sh
cd /app/backend/

yes | python3 manage.py makemigrations # This is a development thing so I don't have to run it manually, but will be removed in production
yes | python3 manage.py migrate
# yes | python manage.py loaddata categories

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@admin.com', 'admin')" | python3 manage.py shell

python3 manage.py runserver 0.0.0.0:8000