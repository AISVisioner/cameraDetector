import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_token():
    # device id - db 참조
    data = {
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD')
    }
    response=''
    try:
        response = requests.post(f'{os.getenv("BASEURL")}/auth/token/login/', data=data)
    except:
        print('error')
    my_token = response.json()['auth_token']
    print(my_token)

    return my_token