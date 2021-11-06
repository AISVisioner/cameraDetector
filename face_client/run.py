import sys
import cv2 as cv
import face_recognition # depencancy on dlib
import uuid
import requests
import time
from datetime import datetime, timezone
import os
import pyttsx3

from get_token import get_token

# the number of count of frames with which a visitor is recognized
COUNT = 5
WINDOW_NAME = "cam"


users = {}

# Initialize values of pyttsx3 engine
engine = pyttsx3.init()

engine.setProperty('rate', 180)
rate = engine.getProperty('rate')

engine.setProperty('volume', 0.5)
volume = engine.getProperty('volume')

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# get token to use the web api(you have to provide appropriate environment variables)
MY_TOKEN = get_token()

def main(argv):
    url = None
    # necessary to input extra arguments
    if len(argv) < 1:
        raise ValueError("No input error")
    # You can also use rtsp to capture a video stream
    if argv[0].startswith("rtsp://"):
        url = argv[0]
    else:
        print("Invalid rtsp url. Initializing url as default webcam (0)")
        url = 0
    
    # Generate a VideoCapture instance
    # Select a camera with a parameter(choose 0 to a local webcam)
    cap = cv.VideoCapture(url)
    encodings = [] # face encodings
    matched = False # if a visitor face is recognized
    flag = False # for imshow
    engine.startLoop(False)
    while True:
        # Read one frame with VideoCapture
        ret, frame = cap.read()
        frame_backup = frame.copy() # backup a non-processed image
        # Show a non-processed image
        cv.imshow(WINDOW_NAME, frame)
        if not ret:
            raise ValueError("No frame error")
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Return a list of coordinates of bounding boxes of faces in a screen
        boxes = face_recognition.face_locations(image)
        print(boxes)
        for box in boxes:
            # Show a location of a face with a bounding box
            frame = cv.rectangle(frame, (box[1], box[0]), (box[3], box[2]), (0, 255, 0), 2)
            cv.imshow(WINDOW_NAME, frame)

            # Extract 128 features of a face
            encoding = face_recognition.face_encodings(image, [box])[0]

            # If a face is captured within frames more than or equal to COUNT variable
            if len(encodings) >= COUNT:
                # Compare features of a face in a new frame with existing ones in COUNT frames
                matches = face_recognition.compare_faces(encodings, encoding)
                # Delete features of a face added first
                del encodings[0]
                # If a new face matches all the faces in COUNT frames
                if False not in matches:
                    matched = True
            encodings.append(encoding)
            # break here to capture only the nearest face
            break

        if matched:
            flag = True
            # id = '' for future use?
            current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")
            # name guest_name in the format "guest_current_time_10 digits of uuid" in order to avoid duplicates
            guest_name = f"guest_{current_time}_{str(uuid.uuid4())[:10]}"
            if not os.listdir("./face_client/images") == []:
                os.remove(f"./face_client/images/{os.listdir('./face_client/images')[0]}")
            cv.imwrite(f'./face_client/images/{guest_name}.jpeg', frame_backup)

            # Get a visitor to wait for a while
            print("Please wait until your check-in is verified.")
            engine.say("Please wait until your check-in is verified.")
            engine.iterate()
            _frame = frame.copy()
            cv.putText(_frame, "Please wait until your check-in is verified.", \
                (100,700), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
            cv.imshow(WINDOW_NAME, _frame)
            cv.waitKey(1)
            time.sleep(5)

            #visitor's face picture
            files = {
                'photo': open(f"./face_client/images/{guest_name}.jpeg", 'rb')
            }
            # id: uuid, encoding: 128 dimension, name: randomly created name without duplicates
            data = {
                "id" : str(uuid.uuid4()),
                "encoding" : encoding,
                "name" : guest_name
            }
            response=''
            # post the visitor's data and files to rest api 
            try:
                response = requests.post(f'{os.getenv("BASEURL")}/api/v1/lookup/', \
                    files=files, data=data, headers={'Authorization': f'Token {MY_TOKEN}'})
                response.raise_for_status()
                # If the visitor has visited a while ago
                if response.status_code == 304:
                    print("Your check-in is already verified. Please check in again later.")
                    engine.say("Your check-in is already verified. Please check in again later.")
                    cv.putText(frame, "Your check-in is already verified.", \
                        (200,650), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                    cv.putText(frame, "Please check in again later.", \
                        (280,700), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                    cv.imshow(WINDOW_NAME, frame)
                    cv.waitKey(1)
                    time.sleep(10)
                    continue
            # if any error occurs
            except:
                print(response.headers["date"])
                print("Sorry, an error occurred while accessing the server. Please contact 010-1234-5678 for any inquiries.")
                engine.say("Sorry, an error occurred while accessing the server. Please contact 010-1234-5678 for any inquiries.")
                cv.putText(frame, "Sorry, an error occurred while accessing the server.", \
                    (0,650), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                cv.putText(frame, "Please contact 010-1234-5678 for any inquiries.", \
                    (0,700), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                cv.imshow(WINDOW_NAME, frame)
                cv.waitKey(1)
                time.sleep(10)
                continue

            print(response.json())
            visits_count = response.json()['visits_count']
            guest_name = response.json()['name']
            # if the visitor visits for the first time
            if visits_count == 1:
                print(f"{guest_name}: Welcome your first visit!")
                engine.say(f"Hello! Welcome your first visit!")
                # engine.runAndWait()
                cv.putText(frame, f"{guest_name}:", \
                    (100,650), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                cv.putText(frame, f"Welcome your first visit!", \
                    (300,700), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
            # if the visitor has visited before
            elif visits_count > 1:
                print(f"{guest_name}: Welcome your {visits_count}th visit!")
                engine.say(f"Hello! Welcome your {visits_count}th visit!")
                # engine.runAndWait()
                cv.putText(frame, f"{guest_name}:", \
                    (100,650), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                cv.putText(frame, f"Welcome your {visits_count}th visit!", \
                    (300,700), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
            cv.imshow(WINDOW_NAME, frame)
            encodings.clear()
        matched = False

        # Break if k number is 27(ESC) after waiting for a key input for 1ms
        k = cv.waitKey(1)
        if k == 27:
            break
        if flag == True:
            engine.iterate()
            time.sleep(10)
            flag = False

    # Stop the engine
    engine.endLoop()
    engine.stop()
    # Release the video object and close the window
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv[1:])