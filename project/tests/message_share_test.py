"""
message/share/v1 tests.
Written By: Daniel Wang (z5312741).
Date written: April 2022.
Tutorial Class: COMP1531 H13B ANT.
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
    return requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "#McLarenWIN", "name_first": "dan", "name_last": "ricciardo"})

@pytest.fixture()
def register_user2():
    return requests.post(f"{URL}/auth/register/v2", json = {"email": "Charles@gmail.com",
    "password": "Evolution", "name_first": "Charles", "name_last": "Darwin"})

def test_invalid_token():
    response = requests.post(f"{URL}/message/share/v1", json = {"token": "u1_token",
    "og_message_id": 1, "message": "I'll pull you in", "channel_id": -1, "dm_id": 1})
    assert response.status_code == 403


def test_message_share_v1_valid_sendToDm(clear, register_user1, register_user2):
    """
    message/share/v1 test.
    Case: Message sent to dm successfully.
    """

    u1_token = register_user1.json()["token"]

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
    "channel_id": ch_id, "message": "Like a moth to a flame"})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to dm.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": "I'll pull you in", "channel_id": -1, "dm_id": dm_id})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["shared_message_id"] != msg_id

    response = requests.get(f"{URL}/dm/messages/v1", params = {"token": u1_token,
    "dm_id": dm_id, "start": 0})
    response_data = response.json()
    assert "Like a moth to a flame" in response_data["messages"][0]["message"]
    assert "I'll pull you in" in response_data["messages"][0]["message"]

def test_message_share_v1_valid_sendToChannel(clear, register_user1):
    """
    message/share/v1 test.
    Case: Message sent to channel successfully.
    """

    u1_token = register_user1.json()["token"]

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

    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "Sometimes, all I think about is you"})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to channel.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": "Late nights in the middle of June", "channel_id": ch_id, "dm_id": -1})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["shared_message_id"] != msg_id

    response = requests.get(f"{URL}/channel/messages/v2", params = {"token": u1_token,
    "channel_id": int(ch_id), "start": 0})
    response_data = response.json()
    assert "Sometimes, all I think about is you" in response_data["messages"][0]["message"]
    assert "Late nights in the middle of June" in response_data["messages"][0]["message"]

def test_message_share_v1_valid_emptyMessage(clear, register_user1):
    """
    message/share/v1 test.
    Case: Empty message.
    """
    u1_token = register_user1.json()["token"]

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

    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I was wondering what would break first — your spirit...or your body."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to channel.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": "", "channel_id": ch_id, "dm_id": -1})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["shared_message_id"] != msg_id

    response = requests.get(f"{URL}/channel/messages/v2", params = {"token": u1_token,
    "channel_id": ch_id, "start": 0})
    response_data = response.json()
    assert "I was wondering what would break first — your spirit...or your body." == response_data["messages"][0]["message"]

def test_message_share_v1_invalid_invalidIDs(clear, register_user1):
    """
    message/share/v1 test.
    Case: both channel_id and dm_id are invalid.
    """
    u1_token = register_user1.json()["token"]

    # Creating channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "50,000 people used to live here."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to channel.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": "Now it's a ghost town...", "channel_id": -1, "dm_id": -1})
    response_data = response.json()
    assert response.status_code == 400

def test_message_share_v1_invalid_noIDsNegativeOne(clear, register_user1):
    """
    message/share/v1 test.
    Case: Neither channel_id or dm_id are -1.
    """
    u1_token = register_user1.json()["token"]

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
    "channel_id": ch_id, "message": "Perhaps a lunatic was simply a minority of one."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to dm.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": "Big Brother is Watching You.", "channel_id": ch_id, "dm_id": dm_id})
    assert response.status_code == 400

def test_message_share_v1_msgIDInvalid(clear, register_user1, register_user2):
    """
    message/share/v1 test.
    Case: og_message_id does not refer to a valid message in a channel/DM user has joined.
    """
    u1_token = register_user1.json()["token"]
    u2_token = register_user2.json()["token"]

    # Creating a channel w/ owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch1_id = response_data["channel_id"]

    # Sending messages to channel 1.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch1_id, "message": "GLaDOS: Well, this is the part where he kills us."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sharing message to dm.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u2_token,
    "og_message_id": msg_id, "message": "Wheatly: Hello! This is the part where I kill you!", "channel_id": -1, "dm_id": dm_id})
    assert response.status_code == 400

def test_message_share_v1_message_length_greater_than_1000(clear, register_user1):
    """
    message/share/v1 test.
    Case: length of message is more than 1000 characters.
    """
    u1_token = register_user1.json()["token"]

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
    "channel_id": ch_id, "message": "Seahaven is the way the world should be."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Sharing message to dm.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u1_token,
    "og_message_id": msg_id, "message": """aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaa""", "channel_id": -1, "dm_id": dm_id})
    assert response.status_code == 400

def test_message_share_v1_user_has_not_joined_dm(clear, register_user1, register_user2):
    """
    message/share/v1 test.
    Case: authorised user has not joined the dm they are trying to share the message to.
    """
    u1_token = register_user1.json()["token"]
    u2_token = register_user2.json()["token"]

    # Creating channel w/ owner user1 and member user 2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/join/v2", json = {"token": u2_token,
    "channel_id": ch_id})

    # Sending messages to channel.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": "Seahaven is the way the world should be."})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": []})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Attempting to share message to dm as user 2 who is not a part of the dm.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u2_token,
    "og_message_id": msg_id, "message": "Nice to meet you, where you been?", "channel_id": -1, "dm_id": dm_id})
    assert response.status_code == 403

def test_message_share_v1_user_has_not_joined_channel(clear, register_user1, register_user2):
    """
    message/share/v1 test.
    Case: authorised user has not joined the channel they are trying to share the message to.
    """
    u1_token = register_user1.json()["token"]
    u2_token = register_user2.json()["token"]
    u2_id = register_user2.json()["auth_user_id"]

    # Creating channel w/ owner user1 and member user 2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Creating dm w/ owner user1.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending messages to dm.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": "I'm like TT, just like TT"})
    response_data = response.json()
    msg_id = response_data["message_id"]

    # Attempting to share message to channel as user 2 who is not a part of the channel.
    response = requests.post(f"{URL}/message/share/v1", json = {"token": u2_token,
    "og_message_id": msg_id, "message": "Tell me that you'll be my baby", "channel_id": ch_id, "dm_id": -1})
    assert response.status_code == 403