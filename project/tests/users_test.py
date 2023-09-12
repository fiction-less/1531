import pytest

from src.error import InputError, AccessError
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_users_all_v1_invalid_token(clear):
    ''' Passes an invalid token '''

    payload = {"token": "1234"}
    response = requests.get(f'{URL}/users/all/v1', params = payload)

    assert(response.status_code == 403)

def test_users_all_v1_valid(clear):
    ''' Lists five valid users '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@gmail.com",
    "password": "testing2", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "daniel.wang@gmail.com",
    "password": "testing3", "name_first": "Daniel", "name_last": "Wang"})
    response_data = response.json()

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "mingrui.ding@gmail.com",
    "password": "testing4", "name_first": "Mingrui", "name_last": "Ding"})
    response_data = response.json()

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "kelly.xu@gmail.com",
    "password": "testing4", "name_first": "Kelly", "name_last": "Xu"})
    response_data = response.json()

    payload = {"token": token}

    response = requests.get(f'{URL}/users/all/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)

    assert response_data == {'users': [
        	{
        		"u_id": 1,
        		"email": "alyssa.lubrano1@gmail.com",
                "name_first": "Alyssa",
                "name_last": "Lubrano",
                "handle_str": "alyssalubrano",
                "profile_img_url": f'{URL}/imgurl/default.jpg'
        	},
        	{
        	    "u_id": 2,
                "email": "aryanbahinipati1@gmail.com",
                "name_first": "Aryan",
                "name_last": "Bahinipati",
                "handle_str": "aryanbahinipati",
                "profile_img_url": f'{URL}/imgurl/default.jpg'
        	},
        	{
        	    "u_id": 3,
                "email": "daniel.wang@gmail.com",
                "name_first": "Daniel",
                "name_last": "Wang",
                "handle_str": "danielwang",
                "profile_img_url": f'{URL}/imgurl/default.jpg'
        	},
            {
                "u_id": 4,
                "email": "mingrui.ding@gmail.com",
                "name_first": "Mingrui",
                "name_last": "Ding",
                "handle_str": "mingruiding",
                "profile_img_url": f'{URL}/imgurl/default.jpg'
            },
            {
                "u_id": 5,
                "email": "kelly.xu@gmail.com",
                "name_first": "Kelly",
                "name_last": "Xu",
                "handle_str": "kellyxu",
                "profile_img_url": f'{URL}/imgurl/default.jpg'
            }
        ]
    }

def test_channels_listall_v2_no_other_users(clear):
    ''' Returns an empty list since they are no channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    response = requests.get(f'{URL}/users/all/v1', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)

    assert response_data == {'users': [{"u_id": 1, "email": "alyssa.lubrano1@gmail.com",
        "name_first": "Alyssa", "name_last": "Lubrano",
        "handle_str": "alyssalubrano", "profile_img_url": f'{URL}/imgurl/default.jpg'}]}

