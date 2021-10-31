import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_token():
    """
    a function to fetch a token to access REST API

    parameter: no
    return: token(str)
    
    """
    # device id - db 참조
    data = {
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD')
    }
    print(data)
    response=''
    try:
        response = requests.post(f'{os.getenv("BASEURL")}/auth/token/login/', data=data)
    except:
        print('error')
    my_token = response.json()['auth_token']
    print(my_token)

    return my_token