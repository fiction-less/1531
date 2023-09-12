# Tests for other.py
# Written 26/02/22
# by Daniel Wang (z5312741@ad.unsw.edu.au)
# for COMP1531 Major Project


import pytest

from src.data_store import data_store
from flask import request
from src import config
from src.other import clear_v1
import requests

URL = f"http://localhost:{config.port}"

def test_clear_v1_valid():
    '''
    Test for test_clear_v1.
    Valid case (Resets the internal data of the application to its original state)..
    '''
    requests.delete(f"{URL}/clear/v1")
    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]
    user2_id = response_data["auth_user_id"]

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    user3_token = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Joining user 3 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user3_token,
    "channel_id": channel_id})
    
    # Creating dm with user 1 and 2.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": user_token,
    "u_ids": [user2_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending dm message as user 2.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": user2_token,
    "dm_id": dm_id, "message": "IT'S LIGHTS OUT AND AWAY WE GO 🏎️🏎️🏎️"})

    # Clearing data store.
    response = requests.delete(f"{URL}/clear/v1")
    response_data = response.json()
    assert response.status_code == 200
    assert response_data == {}