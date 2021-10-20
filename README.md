# cameraDetector
카메라를 이용해 방문자를 식별하고 인사를 하는 키오스크를 개발

**Single Page Application built with Django, Django REST Framework and Vue JS**

## Hot to set up the project to run on your local machine?

#### Create a new Python Virtual Environment:
```
python3 -m venv venv
```

#### Activate the environment and install all the Python/Django dependencies:

```
source ./venv/bin/activate
pip3 install -m ./requirements.txt
```

#### Apply the migrations as usual.

```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

#### Time to install the Vue JS dependencies:
```
cd cameraDetector/frontend
npm install
```

#### Run Vue JS Development Server:
```
npm run serve
```

#### Run Django's development server:
```
python manage.py runserver
```

#### Open up Chrome and go to 127.0.0.1:8000 and the app is now running in development mode!