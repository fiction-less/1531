"""
Tests for notifications functions.
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
    return requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "#McLarenWIN", "name_first": "dan", "name_last": "ricciardo"})

@pytest.fixture()
def register_user2():
    return requests.post(f"{URL}/auth/register/v2", json = {"email": "Charles@gmail.com",
    "password": "Evolution", "name_first": "Charles", "name_last": "Darwin"})

"""
notifications/get/v1 tests.
"""
def test_notifications_get_v1_valid_added_to_dm_notified(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified when added to a dm.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating dm w/ owner user1 and user2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

def test_notifications_get_v1_valid_added_to_channel_notified(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: user is notified when added to a channel
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/invite/v2", json = {"token": u1_token,
    "channel_id": ch_id, "u_id": u2_id})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

def test_notifications_get_v1_valid_tags_in_channel(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified when tagged in a channel.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/join/v2", json = {"token": u2_token,
    "channel_id": ch_id})

    # Tagging user2 in a message as user1.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": f"@charlesdarwin Revenge is a dish best served cold"})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    print(response_data)
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

def test_notifications_get_v1_valid_tags_in_dm(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified when tagged in a dm.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating dm w/ owner user1 and member user2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Tagging user2 in a message as user1.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u1_token,
    "dm_id": dm_id, "message": f"@charlesdarwin Downward is the only way forward"})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 2

def test_notifications_get_v1_valid_multiple_tags(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified only once when tagged multiple times.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/join/v2", json = {"token": u2_token,
    "channel_id": ch_id})

    # Tagging user2 in a message as user1.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": f"@charlesdarwin@charlesdarwin@charlesdarwin THE FATHER OF EVOLUTION"})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

def test_notifications_get_v1_valid_can_tag_self(clear, register_user1):
    data = register_user1.json()
    u1_token = data["token"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # user1 tags self.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
    "channel_id": ch_id, "message": f"@danricciardo Drive!"})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u1_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

# Uncomment when react functions get implemented.
'''
def test_notifications_get_v1_valid_reacted_in_channel(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified when their channel. message gets reacted to.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/invite/v2", json = {"token": u2_token,
    "channel_id": ch_id, "u_id": u2_id})

    # Sending a message in the channel as user2.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": u2_token,
    "channel_id": ch_id, "message": f"Don't stop believin'"})
    msg_id = response.json()["message_id"]

    # Reacting to message as user1.
    response = requests.post(f"{URL}/message/react/v1", json = {"token": u1_token,
    "message_id": msg_id, "react_id": 1})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 2

def test_notifications_get_v1_valid_reacted_in_dm(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is notified when their dm message gets reacted to.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating dm w/ owner user1 and member user2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending a message in the dm as user2.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": u2_token,
    "dm_id": dm_id, "message": f"Don't stop believin'"})
    msg_id = response.json()["message_id"]

    # Reacting to message as user1.
    response = requests.post(f"{URL}/message/react/v1", json = {"token": u1_token,
    "message_id": msg_id, "react_id": 1})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 1

'''

def test_notifications_get_v1_valid_multiple_notifications(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: Tests that 20 notifications are sent if there are more than 20 notifications. Also tests they are in order of most recent to least recent.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_token = data["token"]
    u2_id = data["auth_user_id"]

    # Creating channel w/ owner user1 and member user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": u1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]
    response = requests.post(f"{URL}/channel/invite/v2", json = {"token": u1_token,
    "channel_id": ch_id, "u_id": u2_id})

    for i in range(30):
        # Tagging user2 in a message as user1.
        response = requests.post(f"{URL}/message/send/v1", json = {"token": u1_token,
        "channel_id": ch_id, "message": f"@charlesdarwin {i}"})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": u2_token})
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 20

    # Testing order. (most recent to least recent)
    i = 29
    for noti in response_data["notifications"]:
        assert noti["notification_message"] == f"charlesdarwin tagged you in channel1: @charlesdarwin {i}"
        i -= 1

def test_notifications_get_v1_invalid_token(clear, register_user1, register_user2):
    """
    notifications/get/v1 test.
    Case: User is not notified if the token is invalid.
    """
    data = register_user1.json()
    u1_token = data["token"]

    data = register_user2.json()
    u2_id = data["auth_user_id"]

    # Creating dm w/ owner user1 and member user2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": u1_token,
    "u_ids": [u2_id]})

    # Getting notifications.
    response = requests.get(f"{URL}/notifications/get/v1", params = {"token": "SuperMario64"})
    assert response.status_code == 403