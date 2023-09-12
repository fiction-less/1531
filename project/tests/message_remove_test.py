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

def test_invalid_token(clear):

    remove_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': "invalid token",
        'message_id': -1,
        })

    assert remove_resp.status_code == 403


def test_remove_channel_message(clear):

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    owner = user_resp.json()
    owner_token = owner['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": owner_token,
            "name": "HaydensChannel",
            "is_public": True
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    payload = {'token': owner_token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    messages = response.json()

    assert response.status_code == 200
    print(response.json())
    assert messages['messages'][0]['message'] == "valid message"

    requests.delete(f"{URL}/message/remove/v1", json = {
        'token': owner_token,
        'message_id': message_id,
        })

    payload1 = {'token': owner_token, 'channel_id': channel_id, 'start': 0}
    response1 = requests.get(f"{URL}/channel/messages/v2", params = payload1)
    messages1 = response1.json()
    print(response1.json())

    assert messages1['messages'] == []


def test_invalid_message_id(clear):
    '''message_id does not exist'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    owner = user_resp.json()
    owner_token = owner['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": owner_token,
            "name": "HaydensChannel",
            "is_public": True
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    requests.post(f'{URL}/channel/join/v2', json = {"token": owner_token,
    "channel_id": channel_id})

    requests.post(f"{URL}/message/send/v1", json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': "valid message"})

    remove_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': owner_token,
        'message_id': 100,
        })

    assert remove_resp.status_code == 400

def test_access_error_channel(clear):
    '''channel user removing has no owner permissions and is not the sender'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    owner = user_resp.json()
    owner_token = owner['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden1@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user1 = user_resp1.json()
    token1 = user1['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": owner_token,
            "name": "HaydensChannel",
            "is_public": True
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    requests.post(f'{URL}/channel/join/v2', json = {"token": token1,
    "channel_id": channel_id})

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    remove_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': token1,
        'message_id': message_id,
        })

    assert remove_resp.status_code == 403


def test_access_error_DM(clear):
    '''the user have no owners permissions to remove this DM'''

    list_uid = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydenssss@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    dm_owner = dm_owner_resp.json()
    dm_owner_token = dm_owner['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']
    uid = user['auth_user_id']
    list_uid.append(uid)


    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": dm_owner_token,
            "u_ids": list_uid,
        })
    dm = dm_resp.json()
    dm_id = dm['dm_id']

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": dm_owner_token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    edit_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': "Valid message2"
        })

    assert edit_resp.status_code == 403

def test_message_not_in_DM(clear):
    '''message to be removed is no in the DM the use is in '''

    list_uid = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydenssss@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    dm_owner = dm_owner_resp.json()
    dm_owner_token = dm_owner['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": dm_owner_token,
            "u_ids": list_uid,
        })
    dm = dm_resp.json()
    dm_id = dm['dm_id']

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": dm_owner_token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    edit_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': "Valid message2"
        })

    assert edit_resp.status_code == 400

def test_message_not_in_channel(clear):
    '''message to be removed is not in channel the user is part of '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden2@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user1 = user_resp1.json()
    token1 = user1['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": False
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    requests.post(f'{URL}/channels/create/v2', json = {
            "token": token1,
            "name": "JakesChannel",
            "is_public": False
        })

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    remove_resp = requests.delete(f"{URL}/message/remove/v1", json = {
        'token': token1,
        'message_id': message_id,
        })

    assert remove_resp.status_code == 400



