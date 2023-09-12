'''
Written 18/03/22
by Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

from email import message
import pytest
import time

from flask import request
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_invalid_dm_id(clear):

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
        "password": "nooooo",
        "name_first": "Hayden",
        "name_last": "Smith"})

    owner = dm_owner_resp.json()
    token = owner['token']

    response = requests.post(f"{URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': "nope",
        'message': "yolo",
        'time_sent': time.time() + 1
        })

    assert response.status_code == 400

def test_invalid_message(clear):
    '''test message cant be too long or too short'''

    list_uids = []

    dm_owner_resp = requests.post(f'{URL}/auth/register/v2', json = {
        "email": "Hayden@gmail.com",
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

    invalid_message = "i"*1001
    response = requests.post(f'{URL}/message/sendlaterdm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": invalid_message,
            "time_sent": time.time() + 20})

    assert response.status_code == 400


def test_invalid_token(clear):
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

    response = requests.post(f"{URL}/message/sendlaterdm/v1", json = {
        'token': "invalid token",
        "dm_id": dm_id,
        "message": "hi",
        "time_sent": time.time() + 20})

    assert response.status_code == 403



def test_invalid_time(clear):
    '''time is in the past'''

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

    response = requests.post(f'{URL}/message/sendlaterdm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": "I love comp1531!",
            "time_sent": time.time() - 100})

    assert response.status_code == 400


def test_valid_time(clear):
    '''test time is valid + that message id is NOT yet resgister '''

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

    response = requests.post(f'{URL}/message/sendlaterdm/v1', json = {
            "token": token,
            "dm_id": dm_id,
            "message": "I love comp1531!",
            "time_sent": time.time() + 0.5})

    message_id = response.json()

    payload = {'token': token, 'dm_id': dm_id, 'start': 0}
    response = requests.get(f"{URL}/dm/messages/v1", params = payload)
    dm_messages = response.json()
    print(dm_messages)

    assert response.status_code == 200
    assert len(dm_messages['messages']) == 0
    assert message_id == {'message_id': 1}

    # have to give it at least 1 second before the message send executes properly
    time.sleep(1.5)

    payload1 = {'token': token, 'dm_id': dm_id, 'start': 0}
    response1 = requests.get(f"{URL}/dm/messages/v1", params = payload1)
    dm_messages1 = response1.json()
    print(dm_messages1)

    assert len(dm_messages1['messages']) == 1
    assert dm_messages1['messages'][0]['message_id'] == 1

    response = requests.post(f"{URL}/message/senddm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': "Time to learn"
        })

    data = response.json()
    assert data == {'message_id': 2}



def test_user_not_in_dm():
    '''user attempting to send when not part of channel'''
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

    response = requests.post(f'{URL}/message/sendlaterdm/v1', json = {
            "token": non_member_token,
            "dm_id": dm_id,
            "message": "I love comp1531!",
            "time_sent": time.time() + 0.5})


    assert(response.status_code == 403)


