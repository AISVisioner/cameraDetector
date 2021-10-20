import sys
import cv2 as cv
import face_recognition # depencancy on dlib
import uuid

COUNT = 5

users = {}
# user = {"uuid-1231-123123": [.1232345, .23456734]}

def main(argv):
    url = None
    if len(argv) < 1:
        raise ValueError("No input error")
    if argv[0].startswith("rtsp://"):
        url = argv[0]
    else:
        print("Invalid rtsp url. Initializing url as default webcam (0)")
        url = 0
    
    cap = cv.VideoCapture(url)
    encodings = []
    matched = False
    while True:
        ret, frame = cap.read()
        if not ret:
            raise ValueError("No frame error")
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(image)
        for box in boxes:
            encoding = face_recognition.face_encodings(image, [box])[0]
            if len(encodings) >= COUNT:
                matches = face_recognition.compare_faces(encodings, encoding)
                del encodings[0]
                if False not in matches:
                    matched = True
            encodings.append(encoding)
            break

        if matched:
            registered = False
            user_matched = face_recognition.compare_faces(list(users.values()), encoding)
            for i, user_matched in enumerate(user_matched):
                if user_matched:
                    print(f'matched no.{i} {list(users)[i]}')
                    registered = True
            if not registered:
                user_id = str(uuid.uuid4())
                users[user_id] = encoding
                print(f'new user {user_id}')

        matched = False

if __name__ == "__main__":
    main(sys.argv[1:])