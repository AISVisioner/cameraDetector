import sys
import cv2 as cv
import face_recognition # depencancy on dlib
import uuid
import requests
import numpy as np
import time
from datetime import datetime, timezone
import os
import re
import base64

from get_token import get_token

COUNT = 5
WINDOW_NAME = "cam"

users = {}
# user = {"uuid-1231-123123": [.1232345, .23456734]}

# cv.namedWindow('webcam', cv.WND_PROP_FULLSCREEN)
# cv.setWindowProperty('webcam', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

MY_TOKEN = get_token()

def main(argv):
    url = None
    if len(argv) < 1:
        raise ValueError("No input error")
    if argv[0].startswith("rtsp://"):
        url = argv[0]
    else:
        print("Invalid rtsp url. Initializing url as default webcam (0)")
        url = 0
    
    # VideoCaptureのインスタンスを作成する。
    # 引数でカメラを選べれる。(0はローカルのウェブカメラ)
    cap = cv.VideoCapture(url)
    encodings = []
    matched = False
    while True:
        # VideoCaptureから1フレーム読み込む
        ret, frame = cap.read()
        frame_backup = frame.copy()
        # 加工なし画像を表示する
        cv.imshow(WINDOW_NAME, frame)
        if not ret:
            raise ValueError("No frame error")
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # 画面内に映っている顔のバウンディングボックスの座標タプルを個数分リストで返す。
        boxes = face_recognition.face_locations(image)
        print(boxes)
        for box in boxes:
            # 顔の位置をバウンディングボックスで表示
            color = tuple(map(int, np.random.choice(range(256), size=3)))
            frame = cv.rectangle(frame, (box[1], box[0]), (box[3], box[2]), color, 2)
            cv.imshow(WINDOW_NAME, frame)

            # 128個の顔の特徴点を抽出
            encoding = face_recognition.face_encodings(image, [box])[0]

            # 顔がCOUNTフレーム数以上カメラに映った場合
            if len(encodings) >= COUNT:
                # 新しいフレームに映った顔と既存のCOUNTフレーム数の特徴を比較
                matches = face_recognition.compare_faces(encodings, encoding)
                # 一番古い顔の特徴量を削除
                del encodings[0]
                # 新しい顔が既存のCOUNTフレーム数中の顔全てと一致する場合
                if False not in matches:
                    matched = True
            encodings.append(encoding)
            # 一番近くで映っている顔のみを拾うため、ここでbreakする。
            break

        if matched:
            id = ''
            current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")
            guest_name = f"guest_{current_time}"
            if not os.listdir("./images") == []:
                os.remove(f"./images/{os.listdir('./images')[0]}")
            cv.imwrite(f'./images/{guest_name}.jpg', frame_backup)
            print("Checking verification")
            time.sleep(2)
            # with open(f"./images/{guest_name}.jpg", 'rb') as img_file:
            #     encoded_photo = base64.b64encode(img_file.read())

            # try:
            #     response = requests.get(f'{os.getenv("BASEURL")}/api/v1/lookup/', headers={'Authorization': f'Token {MY_TOKEN}'})
            # except:
            #     print('error')
            # print(response.json())

            files = {
                'photo': open(f"./images/{guest_name}.jpg", 'rb')
            }
            data = {
                "id" : str(uuid.uuid4()),
                "encoding" : encoding,
                "name" : guest_name
            }
            response=''
            try:
                response = requests.post(f'{os.getenv("BASEURL")}/api/v1/lookup/', files=files, data=data, headers={'Authorization': f'Token {MY_TOKEN}'})
                response.raise_for_status()
            except:
                print(response.headers["date"])
                print("Internet connection error!")
            print(response.json())
            exit()
            # visits_count = response
            # if visits_count == 1:
            #     print(f"{guest_name}: Welcome your first visit!")
            # elif visits_count > 1:
            #     print(f"{guest_name}: Welcome your {visits_count}th visit!")


            registered = False
            # my_headers = {
            #     "name" : guest_name
            # }
            # try:
            #     response = requests.get('http://localhost:8000/api/v1/lookup/')
            # except:
            #     print("Internet connection error!")
            # users = response["result"]
            user_matched = face_recognition.compare_faces(list(users.values()), encoding)
            print("a", user_matched)
            # edframe = frame
            for i, user_matched in enumerate(user_matched):
                if user_matched:
                    cv.putText(frame, f'matched no.{i} {list(users)[i]}', (0,50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                    print(f'matched no.{i} {list(users)[i]}')
                    registered = True
            # 登録されていないユーザーの場合
            if not registered:
                user_id = str(uuid.uuid4())
                users[user_id] = encoding
                cv.putText(frame, f'new user {user_id}', (0,50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv.LINE_AA)
                print(f'new user {user_id}')
            cv.imshow(WINDOW_NAME, frame)
        matched = False

        # キー入力を1ms待って、k が27（ESC）だったらBreakする
        k = cv.waitKey(1)
        if k == 27:
            break

    # キャプチャをリリースして、ウィンドウをすべて閉じる
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv[1:])