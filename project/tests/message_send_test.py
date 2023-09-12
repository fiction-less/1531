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

## message send tests

def test_invalid_channel(clear):

    '''channel is invalid'''
    user_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    user = user_resp.json()
    token = user['token']

    invalid_chnnl_id = 9000

    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': invalid_chnnl_id,
        'message': "Time to learn"
        })

    assert response.status_code == 400


def test_invalid_token(clear):
    '''invalid token '''

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

    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': "invalid token",
        'channel_id': channel_id,
        'message': "Time to learn"})

    assert response.status_code == 403


def test_message_too_long(clear):
    '''tests message of len > 1000 '''
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

    message = "i"*1002
    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message})

    assert response.status_code == 400

def test_empty_string(clear):
    '''tests message of len < 1 '''
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

    message = ""
    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message})

    assert response.status_code == 400

def test_member_not_part_of_channel(clear):
    '''valid channel, user not part of it'''

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

    response = requests.post(f"{URL}/message/send/v1", json = {
        'token': token1,
        'channel_id': channel_id,
        'message': "Ahoy there"} )

    assert(response.status_code == 403)




