# cameraDetector
### Developing a kiosk which recognizes visitors and greets using a camera.
<hr>
<br>

**Single Page Application built with Django, Django REST Framework and Vue JS**
![kiosk_description](https://user-images.githubusercontent.com/50127194/138567761-d1cca4db-c9dc-4629-9461-74f805cc9772.png)

## How to set up the project to run on your local machine?

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
cd cameraDetector/backend
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
cd cameraDetector/backend
python3 manage.py runserver
```

#### Open up Chrome and go to 127.0.0.1:8000 and the app is now running in development mode!