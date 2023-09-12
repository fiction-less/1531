'''
Written 18/03/22
by Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

import time
import threading
from flask import request
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_invalid_token(clear):
    '''invalid token '''

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
    print(channel_id)

    response = requests.post(f"{URL}/message/sendlater/v1", json = {
        'token': "invalid token",
        'channel_id': channel_id,
        'message': "yolo",
        'time_sent': time.time()
        })

    assert response.status_code == 403

def test_invalid_channel_id(clear):
    '''channel is invalid'''
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    invalid_channel_id = 9000

    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token,
            "channel_id": invalid_channel_id,
            "message": "I love comp1531!",
            "time_sent": time.time() + 100})

    assert response.status_code == 400


def test_invalid_message(clear):
    '''test message cant be too long or too short'''

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


    invalid_message = "i"*1001
    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": invalid_message,
            "time_sent": time.time() + 20})

    assert response.status_code == 400

    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "",
            "time_sent": time.time() + 20})

    assert response.status_code == 400


def test_invalid_time(clear):
    '''time is in the past'''

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

    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "I love comp1531!",
            "time_sent": time.time() - 1})

    assert response.status_code == 400


def test_valid_time(clear):
    '''test time is valid + that message id is NOT yet resgister '''

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

    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token,
            "channel_id": channel_id,
            "message": "I love comp1531!",
            "time_sent": time.time() + 0.5})

    message_id = response.json()
    payload = {'token': token, 'channel_id': channel_id, 'start': 0}
    response = requests.get(f"{URL}/channel/messages/v2", params = payload)
    chan_messages = response.json()
    print(chan_messages)

    assert response.status_code == 200
    assert len(chan_messages['messages']) == 0
    assert message_id == {'message_id': 1}

    # have to give it at least 1 second before the message send executes properly
    time.sleep(1.5)

    payload1 = {'token': token, 'channel_id': channel_id, 'start': 0}
    response1 = requests.get(f"{URL}/channel/messages/v2", params = payload1)
    chan_messages1 = response1.json()
    print(chan_messages1)

    assert len(chan_messages1['messages']) == 1
    assert chan_messages1['messages'][0]['message_id'] == 1

    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': "Time to learn"
        })

    data = response.json()
    assert data == {'message_id': 2}


def test_user_not_in_channel(clear):
    '''user attempting to send when not part of channel'''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"
        })

    user = user_resp.json()
    token = user['token']

    user_resp1 = requests.post(f'{URL}/auth/register/v2', json = {
            "email": "Jake@gmail.com",
            "password": "nooooo",
            "name_first": "Jake",
            "name_last": "Renzella"
            })

    user1 = user_resp1.json()
    token1 = user1['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {
            "token": token,
            "name": "HaydensChannel",
            "is_public": True})

    channel = chan_resp.json()
    channel_id = channel['channel_id']

    response = requests.post(f'{URL}/message/sendlater/v1', json = {
            "token": token1,
            "channel_id": channel_id,
            "message": "I love comp1531!",
            "time_sent": time.time() + 0.5})


    assert(response.status_code == 403)





