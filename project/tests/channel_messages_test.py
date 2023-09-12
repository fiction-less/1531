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


def test_invalid_channel_id(clear):
    '''channel is invalid'''
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    invalid_chnnl_id = 9000

    payload = {'token': token, 'channel_id': invalid_chnnl_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)

    assert response.status_code == 400

def test_invalid_token(clear):
    '''invalid token'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    payload = {'token': "invalid token", 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)

    assert response.status_code == 403


def test_user_not_in_channel(clear):
    '''valid channel, user not part of it'''
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
            "email": "Jake@gmail.com",
            "password": "nooooo",
            "name_first": "Jake",
            "name_last": "Renzella"})

    user1 = user_resp1.json()
    token1 = user1['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    payload = {'token': token1, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    assert(response.status_code == 403)

def test_invalid_start(clear):
    '''test if start is invalid'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
             "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    payload = {'token': token, 'channel_id': channel_id, 'start': -1}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    assert(response.status_code == 400)


def test_start_greater_than_messages(clear):
    '''start is greater than total num of messages '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
             "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']


    payload = {'token': token, 'channel_id': channel_id, 'start': 10}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    assert(response.status_code == 400)


def test_no_messages(clear):
    '''mo messages/most recent message has been returned'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    payload = {'token': token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    assert response.status_code == 200

    res = response.json()
    assert res == {
        'messages': [],
        'start': 0,
        'end': -1
    }


def test_messages_sent_same_person(clear):
    '''2 messages in same channel by same person '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']
    uid = user['auth_user_id']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    send_resp = requests.post(f'{URL}/message/send/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "I love comp1531!"})

    msg_send = send_resp.json()
    message_id = msg_send['message_id']

    send_resp1 = requests.post(f'{URL}/message/send/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "I hate comp1531"})

    msg_send1 = send_resp1.json()
    message_id1 = msg_send1['message_id']

    payload = {'token': token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    response_data = response.json()
    assert response.status_code == 200
    print(response_data)
    assert response_data['messages'][0]['message_id'] == message_id1
    assert response_data['messages'][0]['u_id'] == uid
    assert response_data['messages'][0]['message'] == "I hate comp1531"
    assert response_data['messages'][1]['message_id'] == message_id
    assert response_data['messages'][1]['u_id'] == uid
    assert response_data['messages'][1]['message'] == "I love comp1531!"


def test_messages_sent_diff_person(clear):
    '''messages in same channel by different ppl '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']
    uid = user['auth_user_id']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
            "email": "Jake@gmail.com",
            "password": "nooooo",
            "name_first": "Jake",
            "name_last": "Renzella"})

    user1 = user_resp1.json()
    token1 = user1['token']
    uid1 = user1['auth_user_id']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
            "email": "Jakee@gmail.com",
            "password": "nooooo",
            "name_first": "Jake",
            "name_last": "Renzella"})

    user2 = user_resp1.json()
    token2 = user2['token']
    uid2 = user2['auth_user_id']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    requests.post(f'{URL}/channel/join/v2', json = {
            "token": token1,
            "channel_id": channel_id})

    requests.post(f'{URL}/channel/join/v2', json = {
            "token": token2,
            "channel_id": channel_id})

    requests.post(f'{URL}/message/send/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "I love comp1531!"})

    requests.post(f'{URL}/message/send/v1', json = {
            "token": token1,
            "channel_id": channel_id,
            "message": "eh, 2521 is better imo"})

    requests.post(f'{URL}/message/send/v1', json = {
            "token": token2,
            "channel_id": channel_id,
            "message": "..."})


    payload = {'token': token2, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    response_data = response.json()
    assert response.status_code == 200

    print(response_data)
    assert response_data['messages'][0]['message_id'] == 3
    assert response_data['messages'][0]['u_id'] == uid2
    assert response_data['messages'][0]['message'] == "..."
    assert response_data['messages'][1]['message_id'] == 2
    assert response_data['messages'][1]['u_id'] == uid1
    assert response_data['messages'][1]['message'] == "eh, 2521 is better imo"
    assert response_data['messages'][2]['message_id'] == 1
    assert response_data['messages'][2]['u_id'] == uid
    assert response_data['messages'][2]['message'] == "I love comp1531!"



def test_end_is_zero(clear):
    '''when there is 50 messages to return. check end is 0'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    i = 0
    while i < 51:
        requests.post(f'{URL}/message/send/v1', json = {
                    "token": token,
                    "channel_id": channel_id,
                    "message": "I love comp1531!"})
        i += 1

    payload = {'token': token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    response_data = response.json()
    print(response_data)
    assert response.status_code == 200
    assert response_data['end'] == 50


def test_71_messages_non_zero_start(clear):
    '''when there is 50 messages to return. check end is 0'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": False})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    i = 0
    while i < 71:
        requests.post(f'{URL}/message/send/v1', json = {
                    "token": token,
                    "channel_id": channel_id,
                    "message": "I love comp1531!"})
        i += 1

    payload = {'token': token, 'channel_id': channel_id, 'start': 19}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['end'] == 69


    payload1 = {'token': token, 'channel_id': channel_id, 'start': 69}
    response1 = requests.get(f"{URL}/channel/messages/v2", params = payload1)
    response_data1 = response1.json()

    assert response.status_code == 200
    assert response_data1['end'] == -1

