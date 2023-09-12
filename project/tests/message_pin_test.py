'''
Written 11/05/22
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
    '''invalid token '''
    response = requests.post(f"{URL}/message/pin/v1", json = {
        'token': "invalid token",
        'message_id': 1})

    assert response.status_code == 403

def test_already_pinned(clear):

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token,
        'message_id': message_id,
        })
    assert pin_resp.status_code == 200

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token,
        'message_id': message_id,
        })
    assert pin_resp.status_code == 400


def test_message_id_invalid(clear):
    '''message_id does not exist'''

    owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    owner = owner_resp.json()
    owner_token = owner['token']

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': owner_token,
        'message_id': 100,
        })

    assert pin_resp.status_code == 400


def test_global_owner_DM(clear):
    '''global owner whose in DM but not DM owner cant pin DM'''
    list_uid = []

    global_owner = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    g_owner = global_owner.json()
    global_token = g_owner['token']
    global_uid = g_owner['auth_user_id']
    list_uid.append(global_uid)

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydenssss@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    dm_owner = dm_owner_resp.json()
    dm_owner_token = dm_owner['token']

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

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': global_token,
        'message_id': message_id,
        })

    assert pin_resp.status_code == 403


def test_access_error_channel(clear):
    '''channel user pinning has no owner permissions (not global owner and not channelowner) '''

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

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token1,
        'message_id': message_id,
        })

    assert pin_resp.status_code == 403


def test_access_error_DM(clear):
    '''the user have no owners permissions to pin this DM'''

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

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token,
        'message_id': message_id,
        })

    assert pin_resp.status_code == 403

def test_valid_pinned(clear):
    '''test channel onwer, gloabl owner and DM owner can pin messages'''

    list_uid = []

    owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydenssss@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    owner = owner_resp.json()
    owner_token = owner['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

    dm_resp = requests.post(f'{URL}/dm/create/v1', json = {
            "token": owner_token,
            "u_ids": list_uid,
        })
    dm = dm_resp.json()
    dm_id = dm['dm_id']

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": owner_token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': owner_token,
        'message_id': message_id
        })

    assert pin_resp.status_code == 200

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    requests.post(f'{URL}/channel/join/v2', json = {"token": owner_token,
    "channel_id": channel_id})

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token,
        'message_id': message_id,
        })
    assert pin_resp.status_code == 200

    msg_resp1 = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "valid message"})

    message1 = msg_resp1.json()
    message_id1 = message1['message_id']

    pin_resp1 = requests.post(f"{URL}/message/pin/v1", json = {
        'token': owner_token,
        'message_id': message_id1,
        })
    assert pin_resp1.status_code == 200


def test_message_not_in_DM(clear):
    '''message to be pinned is not in the DM the user is in '''

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

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token,
        'message_id': message_id,
        })

    assert pin_resp.status_code == 400

def test_message_not_in_channel(clear):
    '''message to be pinned is not in channel the user is part of '''

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

    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "valid message"})

    message = msg_resp.json()
    message_id = message['message_id']

    pin_resp = requests.post(f"{URL}/message/pin/v1", json = {
        'token': token1,
        'message_id': message_id,
        })

    assert pin_resp.status_code == 400

