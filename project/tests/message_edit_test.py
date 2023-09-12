'''
Written 18/03/22
by Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''


import re
import pytest

from flask import request
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_invalid_token(clear):

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': "invalid_token",
        'message_id': 1,
        'message': "Valid message"
        })

    assert edit_resp.status_code == 403

def test_message_doesnt_exist(clear):
    '''the message does not exist'''
    list_uid = []

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

    requests.post(f'{URL}/message/senddm/v1', json = {
            "token": dm_owner_token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    requests.post(f'{URL}/message/senddm/v1', json = {
            "token": dm_owner_token,
            "dm_id": dm_id,
            "message": "valid message2"
        })

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': dm_owner_token,
        'message_id': 1000,
        'message': "Valid message"
        })

    assert edit_resp.status_code == 400


def test_seams_channel(clear):
    '''seams editing a message in a private channel theyve joined'''
    seams_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    seams_owner = seams_resp.json()
    print(seams_owner)
    seams_token = seams_owner['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user1 = user_resp1.json()
    token1 = user1['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token1,
            "name": "HaydensChannel",
            "is_public": False
        })
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    msg_resp = requests.post(f'{URL}/message/send/v1', json = {
            "token": token1,
            "channel_id": channel_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    join_resp = requests.post(f'{URL}/channel/join/v2', json = {
        "token": seams_token,
        "channel_id": channel_id})

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': seams_token,
        'message_id': message_id,
        'message': "Valid message"
        })

    assert message == {'message_id': message_id}
    assert edit_resp.status_code == 200
    assert join_resp.json() == {}
    assert edit_resp.json() == {}


def test_seams_DM_invalid(clear):
    '''seams editing a message in a DM where theyre NOT the owner'''

    list_uid = []
    seams_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    seams_owner = seams_resp.json()
    seams_token = seams_owner['token']
    seams_uid = seams_owner['auth_user_id']
    list_uid.append(seams_uid)

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
    print(dm)
    dm_id = dm['dm_id']

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    assert message_id == 1
    assert message == {'message_id': 1}

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': seams_token,
        'message_id': message_id,
        'message': "Valid message"
        })

    assert edit_resp.status_code == 403


def test_channel_owner_permissions(clear):
    '''owner of channel editing someone elses message within the channel'''

    onwer_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    owner = onwer_resp.json()
    owner_token = owner['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
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

    join_resp = requests.post(f'{URL}/channel/join/v2', json = {
        "token": token1,
        "channel_id": channel_id})

    assert join_resp.status_code == 200
    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': token1,
        'channel_id': channel_id,
        'message': "valid message"
        })

    message = msg_resp.json()
    print(message)
    message_id = message['message_id']

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': owner_token,
        'message_id': message_id,
        'message': "I have the power to edit your message MWHuAHAHAaHa"
        })

    assert edit_resp.status_code == 200
    assert edit_resp.json() == {}

def test_access_Error_channel(clear):
    '''user without permission attempting to edit someone elses message within the channel'''

    onwer_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    owner = onwer_resp.json()
    owner_token = owner['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
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

    join_resp = requests.post(f'{URL}/channel/join/v2', json = {
        "token": token1,
        "channel_id": channel_id})

    assert join_resp.status_code == 200
    msg_resp = requests.post(f"{URL}/message/send/v1", json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token1,
        'message_id': message_id,
        'message': "I have the power to edit your message MWHuAHAHAaHa"
        })

    assert edit_resp.status_code == 403


def test_DM_owners_permissions(clear):
    '''test a DM owner can edit other users messages'''

    list_uid = []
    seams_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    seams_owner = seams_resp.json()
    seams_uid = seams_owner['auth_user_id']
    list_uid.append(seams_uid)

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
    print("dmid",dm_id)

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    print(message)
    message_id = message['message_id']
    print(message_id)

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': dm_owner_token,
        'message_id': message_id,
        'message': "Valid message2"
        })

    assert edit_resp.status_code == 200


def test_editing_someone_elses_message(clear):
    '''user not part of channel that the message_id exists in '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Haydens@gmail.com",
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
        'message': "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token1,
        'message_id': message_id,
        'message': "Valid message"
        })

    assert edit_resp.status_code == 400

def test_edit_DM_message_invalid(clear):
    '''Dm message exists in a DM the user isnt part of'''

    list_uid = []
    seams_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    seams_owner = seams_resp.json()
    seams_uid = seams_owner['auth_user_id']
    list_uid.append(seams_uid)

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
    print("dmid",dm_id)

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": dm_owner_token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    message_id = message['message_id']


    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': "Valid message2"
        })

    assert edit_resp.status_code == 400

def test_new_channe_message_too_long(clear):
    '''new channel message len > 1000 '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

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

    invalid_message = "YO"*501
    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': invalid_message
        })

    assert edit_resp.status_code == 400


def test_new_message_empty_str(clear):
    '''if edited messaged is empty, message should be deleted'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    user = user_resp.json()
    token = user['token']

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

    empty_message = ""
    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': empty_message
        })

    payload = {'token': token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    messages = response.json()

    assert response.status_code == 200
    assert messages == {'messages': [], 'start': 0, 'end': -1}
    assert edit_resp.json() == {}


def test_valid_channel_message(clear):
    '''editing valid message id from a channel they are in'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    user = user_resp.json()
    token = user['token']

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

    print(msg_resp)
    message = msg_resp.json()
    print(message)
    valid_message_id = message['message_id']

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token,
        'message_id': valid_message_id,
        'message': "Valid message"
        })
    edit_message = edit_resp.json()

    assert edit_message == {}
    assert edit_resp.status_code == 200

def test_valid_DM_message(clear):
    '''editing valid message id from a DM they are in'''

    list_uid = []
    seams_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })
    seams_owner = seams_resp.json()
    seams_uid = seams_owner['auth_user_id']
    list_uid.append(seams_uid)

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
    print("dmid",dm_id)

    msg_resp = requests.post(f'{URL}/message/senddm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": "valid message"
        })

    message = msg_resp.json()
    print(message)
    message_id = message['message_id']
    print(message_id)

    edit_resp = requests.put(f"{URL}/message/edit/v1", json = {
        'token': token,
        'message_id': message_id,
        'message': "Valid message2"
        })

    assert edit_resp.status_code == 200