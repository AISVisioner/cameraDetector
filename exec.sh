docker-compose down -v
docker volume rm cameradetector_static-volume
docker volume rm cameradetector_templates-volume
docker-compose up --build -d
brew install cmake
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 ./face_client/run.py 0