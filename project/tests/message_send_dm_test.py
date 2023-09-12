'''
Written 18/03/22
by Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

from flask import request
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')


def test_invalid_dm_id(clear):
    '''DM_id is invalid'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    invalid_dm_id = 9000

    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': token,
        'dm_id': invalid_dm_id,
        'message': "Time to learn"
        })

    assert response.status_code == 400


def test_invalid_token(clear):
    '''invalid token '''

    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Jajj@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    token = owner['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": token,
            "u_ids": list_uids,
            })

    dm = dm_resp.json()
    dm_id = dm['dm_id']
    assert dm == {'dm_id': 1}

    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': "invalid token",
        'dm_id': dm_id,
        'message': "Time to learn"
        })

    assert response.status_code == 403


def test_message_too_long(clear):
    '''tests message of len > 1000 '''

    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    owner_token = owner['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": owner_token,
            "u_ids": list_uids,
            })

    dm = dm_resp.json()
    dm_id = dm['dm_id']


    invalid_message = "i"*1001
    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': invalid_message})

    print(response)
    assert response.status_code == 400



def test_empty_string(clear):
    '''tests message of len < 1 '''

    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    owner_token = owner['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": owner_token,
            "u_ids": list_uids,
            })

    dm = dm_resp.json()
    dm_id = dm['dm_id']

    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': ""})

    print(response)
    assert response.status_code == 400

def test_member_not_part_of_dm(clear):
    '''valid channel, user not part of it'''
    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    owner_token = owner['token']


    non_member_resp = requests.post(f'{URL}/auth/register/v2', json = {
            "email": "Jake@gmail.com",
            "password": "nooooo",
            "name_first": "Jake",
            "name_last": "Renzella"
            })

    non_member = non_member_resp.json()
    non_member_token = non_member['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": owner_token,
            "u_ids": list_uids,
            })

    dm = dm_resp.json()
    dm_id = dm['dm_id']
    assert dm_id == 1

    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': non_member_token,
        'dm_id': dm_id,
        'message': "Hi there"})

    print(response)

    assert(response.status_code == 403)


def test_valid_dm_send(clear):
    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    owner_token = owner['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Jake@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()

    token = user['token']
    uid = user['auth_user_id']
    list_uids.append(uid)

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Tam@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user1 = user_resp1.json()
    uid1 = user1['auth_user_id']
    list_uids.append(uid1)

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": owner_token,
            "u_ids": list_uids,
            })

    dm = dm_resp.json()
    print(dm)
    dm_id = dm['dm_id']
    assert dm == {'dm_id': 1}

    dm_send_resp = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': "Time to learn"
        })
    dm_message = dm_send_resp.json()
    message_id = dm_message['message_id']

    assert message_id == 1
    assert dm_send_resp.status_code == 200

    payload = {"token": token, 'dm_id': dm_id, 'start': 0}
    dm_msg_resp = requests.get(f'{URL}/dm/messages/v1', params = payload)

    dm_dict = dm_msg_resp.json()

    assert dm_dict['messages'][0]['message_id'] == 1
    assert dm_dict['messages'][0]['u_id'] == 1
    assert dm_dict['messages'][0]['message'] == "Time to learn"
    assert dm_msg_resp.status_code == 200

    requests.post(f"{URL}/message/senddm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': "im really sorry, but i have an outing today"
        })

    payload = {"token": token, 'dm_id': dm_id, 'start': 0}
    dm_msg_resp = requests.get(f'{URL}/dm/messages/v1', params = payload)
    dm_message = dm_msg_resp.json()

    assert dm_message['messages'][0]['message_id'] == 2
    assert dm_message['messages'][0]['u_id'] == 2
    assert dm_message['messages'][0]['message'] == "im really sorry, but i have an outing today"
    assert dm_msg_resp.status_code == 200
