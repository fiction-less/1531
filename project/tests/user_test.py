''' Tests for user.py
Written 21/03/22
by Alyssa Lubrano (z5362292@ad.unsw.edu.au) and Aryan Bahinipati (z5310696@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

from flask import request
from src.error import AccessError, InputError
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_user_profile_v1_invalid_token(clear):
    ''' Passes an invalid token '''


    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    response = requests.get(f'{URL}/user/profile/v1', params = {"token": "1234", "u_id": 1})

    assert(response.status_code == 403)

def test_user_profile_v1_valid_user(clear):
    ''' Valid token and user id '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    response_data = response.json()

    token = response_data['token']
    u_id = response_data['auth_user_id']

    payload = {"token": token, "u_id": u_id}
    response = requests.get(f'{URL}/user/profile/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'user': {'u_id': 1, 'email': 'alyssa.lubrano1@gmail.com',
    'name_first': "Alyssa", 'name_last': "Lubrano", 'handle_str': "alyssalubrano", 
    "profile_img_url": f'{URL}/imgurl/default.jpg'}}

def test_user_profile_v1_invalid_u_id(clear):
    ''' Invalid user id '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token, "u_id": -1}

    response = requests.get(f'{URL}/user/profile/v1', params = payload)

    assert(response.status_code == 400)

def test_user_profile_set_name_v1_invalid_token(clear):
    ''' Passes an invalid token '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    response = requests.put(f'{URL}/user/profile/setname/v1', json = {"token": "1234",
    "name_first": "Aly", "name_last": "Lub"})

    assert(response.status_code == 403)

def test_user_profile_set_name_v1_invalid_characters_small(clear):
    ''' Passes an invalid first and last name (too small) '''


    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/setname/v1", json = {'token': token, 'name_first': "",
    'name_last': ""})

    assert edit_resp.status_code == 400

def test_user_profile_set_name_v1_invalid_characters_big(clear):
    ''' Passes an invalid first and last name (too large) '''


    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    invalid_name = "HI" * 50

    edit_resp = requests.put(f"{URL}/user/profile/setname/v1", json = {'token': token, 'name_first': invalid_name,
    'name_last': invalid_name})

    assert edit_resp.status_code == 400

def test_user_profile_set_name_v1_valid_name_change(clear):
    ''' Passes a valid first and last name '''


    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/setname/v1", json = {'token': token, 'name_first': "Aly",
    'name_last': "Lub"})
    edit_name = edit_resp.json()

    assert edit_resp.status_code == 200
    assert edit_name == {}
    
    payload = {"token": token, "u_id": 1}
    response = requests.get(f'{URL}/user/profile/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'user': {'u_id': 1, 'email': 'alyssa.lubrano1@gmail.com',
    'name_first': "Aly", 'name_last': "Lub", 'handle_str': "alyssalubrano",
    "profile_img_url": f'{URL}/imgurl/default.jpg'}}

def test_user_profile_setmail_v1_invalid_token(clear):
    ''' Passes an invalid token '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    response = requests.put(f'{URL}/user/profile/setemail/v1', json = {"token": "1234",
    "email": "aly.lubrano1@gmail.com"})

    assert(response.status_code == 403)


def test_user_profile_setmail_v1_invalid_email_format(clear):
    ''' Passes an invalid email '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/setemail/v1", json = {'token': token, 'email': "incorrect"})

    assert edit_resp.status_code == 400


def test_user_profile_setmail_v1_invalid_existing_email(clear):
    ''' Passes an existing email '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token_1 = user['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "aly.lubrano1@gmail.com",
    "password": "testing2", "name_first": "Aly", "name_last": "Lubrano"})

    user = user_resp.json()

    edit_resp = requests.put(f"{URL}/user/profile/setemail/v1", json = {'token': token_1, 'email':
    "aly.lubrano1@gmail.com"})

    assert edit_resp.status_code == 400

def test_user_profile_setmail_v1_valid_mail_change(clear):
    ''' editing valid email '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/setemail/v1", json = {'token': token, 'email':
    "aly.lubrano1@gmail.com"})
    edit_name = edit_resp.json()

    assert edit_resp.status_code == 200
    assert edit_name == {}
    
    payload = {"token": token, "u_id": 1}
    response = requests.get(f'{URL}/user/profile/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'user': {'u_id': 1, 'email': 'aly.lubrano1@gmail.com',
    'name_first': "Alyssa", 'name_last': "Lubrano", 'handle_str': "alyssalubrano",
    "profile_img_url": f'{URL}/imgurl/default.jpg'}}

def test_user_profile_sethandle_v1_invalid_token(clear):
    ''' Passes an invalid token '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    response = requests.put(f'{URL}/user/profile/sethandle/v1', json = {"token": "1234",
    "handle_str": "alylubrano"})

    assert(response.status_code == 403)

def test_user_profile_sethandle_v1_invalid_handle_small(clear):
    ''' Passes an invalid handle (too small) '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})


    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/sethandle/v1", json = {'token': token, 'handle_str': "al"})

    assert edit_resp.status_code == 400

def test_user_profile_sethandle_v1_invalid_handle_large(clear):
    ''' Passes an invalid handle (too large) '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    invalid_handle = "aly" * 10

    edit_resp = requests.put(f"{URL}/user/profile/sethandle/v1", json = {'token': token, 'handle_str': invalid_handle})

    assert edit_resp.status_code == 400

def test_user_profile_sethandle_v1_invalid_existing_handle(clear):
    ''' Passes an existing handle '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token_1 = user['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "aly.lubrano1@gmail.com",
    "password": "testing2", "name_first": "Aly", "name_last": "Lubrano"})

    user = user_resp.json()

    edit_resp = requests.put(f"{URL}/user/profile/sethandle/v1", json = {'token': token_1, 'handle_str':
    "alylubrano"})

    assert edit_resp.status_code == 400

def test_user_profile_sethandle_v1_valid_handle_change(clear):
    ''' editing valid email '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token = user['token']

    edit_resp = requests.put(f"{URL}/user/profile/sethandle/v1", json = {'token': token, 'handle_str':
    "alylubrano"})
    edit_name = edit_resp.json()

    assert edit_resp.status_code == 200
    assert edit_name == {}
    
    payload = {"token": token, "u_id": 1}
    response = requests.get(f'{URL}/user/profile/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'user': {'u_id': 1, 'email': 'alyssa.lubrano1@gmail.com',
    'name_first': "Alyssa", 'name_last': "Lubrano", 'handle_str': "alylubrano",
    "profile_img_url": f'{URL}/imgurl/default.jpg'}}

def test_user_profile_uploadphoto_v1_invalid_token(clear):
    ''' Passing invalid token '''
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": "1234",
    "img_url": "http://www.personal.psu.edu/kbl5192/jpg.jpg", "x_start": 0, 
    "y_start": 0, "x_end": 200, "y_end": 200})
    
    assert(response.status_code == 403)

def test_user_profile_uploadphoto_v1_http_status_error(clear):
    ''' Passing invalid url '''
    
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    
    user = user_resp.json()
    token = user['token']
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": token,
    "img_url": "http://www.personal.psu.edu/kbl5192/hello.jpg", "x_start": 0, "y_start": 0, "x_end": 200, "y_end": 200})
    
    assert(response.status_code == 400)

def test_user_profile_uploadphoto_v1_dimensions_not_within(clear):
    ''' Passing dimensions greater than image '''
    
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    
    user = user_resp.json()
    token = user['token']
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": token,
    "img_url": "http://www.personal.psu.edu/kbl5192/jpg.jpg", "x_start": -1, 
    "y_start": -1, "x_end": 100000 , "y_end": 10000})
    
    assert(response.status_code == 400)

def test_user_profile_uploadphoto_v1_start_dimensions_greater_than_end(clear):
    ''' Start dimensions of image greater than end '''
    
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    
    user = user_resp.json()
    token = user['token']
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": token,
    "img_url": "http://www.personal.psu.edu/kbl5192/jpg.jpg", "x_start": 200, 
    "y_start": 200, "x_end": 0 , "y_end": 0})
    
    assert(response.status_code == 400)

def test_user_profile_uploadphoto_v1_not_jpg(clear):
    ''' Start dimensions of image greater than end '''
    
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    
    user = user_resp.json()
    token = user['token']
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": token,
    "img_url": "https://www.pngall.com/wp-content/uploads/11/Yoshi-PNG-Clipart.png",
    "x_start": 0, "y_start": 0, "x_end": 50 , "y_end": 50})
    
    assert(response.status_code == 400)

def test_user_profile_uploadphoto_v1_valid(clear):
    ''' Valid test case '''
    
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    
    user = user_resp.json()
    token = user['token']
    
    response = requests.post(f'{URL}/user/profile/uploadphoto/v1', json = {"token": token,
    "img_url": "http://www.personal.psu.edu/kbl5192/jpg.jpg", "x_start": 0, 
    "y_start": 0, "x_end": 200 , "y_end": 200})
    response_data = response.json()
    
    assert(response.status_code == 200)
    assert response_data == {}  

