''' Tests for channels.py
Written 26/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

from flask import request
from src.error import AccessError, InputError
from src import config
import requests

URL = f'http://localhost:{config.port}'

# Channels_create_v2 Tests:

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

def test_channels_create_v2_invalid_token(clear):
    ''' Passes an invalid token '''

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": "1234",
    "name": "Channel1", "is_public": False})

    assert(response.status_code == 403)

def test_channels_create_v2_invalid_characters_small(clear):
    ''' Channel name is blank '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "", "is_public": False})

    assert(response.status_code == 400)

def test_channels_create_v2_invalid_characters_big(clear):
    ''' Channel name is bigger than 20 characters '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "abcdefghijklmnopqrstuvwxyz", "is_public": False})

    assert(response.status_code == 400)

def test_channels_create_v2_valid_public(clear):
    ''' Channel name is within character range and is public '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'channel_id': 1}

def test_channels_create_v2_valid_private(clear):
    ''' Channel name is within character range and is private '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": False})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'channel_id': 1}


# Channels_list_v2 Tests:

def test_channels_list_v2_invalid_token(clear):
    ''' Passes an invalid token '''

    payload = {"token": "1234"}
    response = requests.get(f'{URL}/channels/list/v2', params = payload)

    assert(response.status_code == 403)

def test_channels_list_v2_no_channels():
    ''' Authorised user is part of no channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    response = requests.get(f'{URL}/channels/list/v2', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'channels': []}


def test_channels_list_v2_one_channel(clear):
    ''' Authorised user is part of 1 channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})

    response = requests.get(f'{URL}/channels/list/v2', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'channels': [{'channel_id': 1, 'name': 'Channel1'}]}

def test_channels_list_v2_many_channels(clear):
    ''' Authorised user is part of 3 channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel2", "is_public": True})
    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel3", "is_public": True})

    response = requests.get(f'{URL}/channels/list/v2', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {'channels': [
        	{
        		'channel_id': 1,
        		'name': 'Channel1'
        	},
        	{
        	    'channel_id': 2,
        	    'name': 'Channel2'
        	},
        	{
        	    'channel_id': 3,
        	    'name': 'Channel3'
        	}
        ]
    }

# Tests for channels_listall_v2.

def test_channels_listall_v2_invalid_token(clear):
    ''' Passes an invalid token '''

    payload = {"token": "1234"}
    response = requests.get(f'{URL}/channels/listall/v2', params = payload)

    assert(response.status_code == 403)

def test_channels_listall_v2_valid(clear):
    ''' Lists three valid channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel2", "is_public": False})
    requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel3", "is_public": True})

    response = requests.get(f'{URL}/channels/listall/v2', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)

    assert response_data == {'channels': [
        	{
        		'channel_id': 1,
        		'name': 'Channel1'
        	},
        	{
        	    'channel_id': 2,
        	    'name': 'Channel2'
        	},
        	{
        	    'channel_id': 3,
        	    'name': 'Channel3'
        	}
        ]
    }

def test_channels_listall_v2_no_channels(clear):
    ''' Returns an empty list since they are no channels '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    response = requests.get(f'{URL}/channels/listall/v2', params = payload)
    response_data = response.json()

    assert(response.status_code == 200)

    assert response_data == {'channels': []}

