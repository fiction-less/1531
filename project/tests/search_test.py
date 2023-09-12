"""
Tests for search functions.
Daniel Wang (z5312741)
COMP1531 H13B ANT.
"""

import pytest
from flask import request
from src.error import AccessError, InputError
from src import config
import requests

URL = f"http://localhost:{config.port}"

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

@pytest.fixture()
def register_user1():
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "#McLarenWIN", "name_first": "dan", "name_last": "ricciardo"})
    return response

"""
Tests for search/v1.
"""

def test_search_v1_valid_query_str(clear):
    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]
    

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the top because it's red."})

    # Retrieving messages specified by a query string.
    response = requests.get(f"{URL}/search/v1", params = {"token": u1_token,
    "query_str": "shirt"})
    response_data = response.json()
    assert len(response_data["messages"]) == 3
    assert response.status_code == 200

def test_search_v1_valid_user_not_in_channel(clear):
    """
    search/v1 test.
    Case: Messages from channels that user is not a part of are not being appened to the 'messages' list.
    """
    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]

    # Registering user2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "Scott@gmail.com",
    "password": "freedom", "name_first": "Scott", "name_last": "Smith"})
    response_data = response.json()
    u2_token = response_data["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": u2_token,
    "channel_id": ch_id})

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's sleek and modern."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's red."})

    # Retrieving messages specified by a query string.
    response = requests.get(f"{URL}/search/v1", params = {"token": u2_token,
    "query_str": "shirt"})
    response_data = response.json()
    assert len(response_data["messages"]) == 3
    assert response.status_code == 200


def test_search_v1_valid_user_not_in_dm(clear):
    """
    search/v1 test.
    Case: Messages from channels that user is not a part of are not being appened to the 'messages' list.
    """
    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]

    # Registering user2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "Scott@gmail.com",
    "password": "freedom", "name_first": "Scott", "name_last": "Smith"})
    response_data = response.json()
    u2_id = response_data["auth_user_id"]
    u2_token = response_data["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1 and member user 2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's red."})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's expensive."})

    # Retrieving messages specified by a query string.
    response = requests.get(f"{URL}/search/v1", params = {"token": u2_token,
    "query_str": "shirt"})
    response_data = response.json()
    assert len(response_data["messages"]) == 3
    assert response.status_code == 200

def test_search_v1_invalidToken(clear):
    """
    search/v1 test.
    Case: Invalid token given.
    """

    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's red."})

    # Attempting to retrieve messages using a invalid token.
    response = requests.get(f"{URL}/search/v1", params = {"token": "invalid token",
    "query_str": "shirt"})
    response_data = response.json()
    assert response.status_code == 403

def test_search_v1_querystr_size_less_than_1(clear):
    """
    search/v1 test.
    Case: querystr size < 1
    """

    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's red."})

    # Attempting to retrieve messages using a querystr size less than 1.
    response = requests.get(f"{URL}/search/v1", params = {"token": "invalid token",
    "query_str": ""})
    response_data = response.json()
    assert response.status_code == 400

def test_search_v1_query_size_bigger_than_1000(clear):
    """
    search/v1 test.
    Case: querystr size > 1000
    """

    # Registering global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    u1_token = response_data["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like this shirt!"})
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "I like the shirt because it's blue."})
    
    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate this shirt!"})
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I hate the shirt because it's red."})

    # Attempting to retrieve messages using a querystr size bigger than 1000.
    response = requests.get(f"{URL}/search/v1", params = {"token": "invalid token",
    "query_str": """aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aa"""})
    response_data = response.json()
    assert response.status_code == 400