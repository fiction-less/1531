"""
Tests for admin functions.
Daniel Wang (z5312741)
COMP1531 H13B ANT.
"""

import pytest
from flask import request
from src.error import AccessError, InputError
from src import config
import requests
from src.data_store import data_store

URL = f"http://localhost:{config.port}"


"""
Tests for admin_userremove_v1.
"""


def test_admin_user_remove_v1_valid():
    """
    Test for admin_user_remove_v1.
    Valid case (user with token successfully removes user with u_id from seams).
    """
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]
    user1_id = response_data["auth_user_id"]


    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]
    user2_id = response_data["auth_user_id"]

    # Registering user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "Kelly@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user3_id = response_data["auth_user_id"]

    # Creating channel with user 2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 1 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user1_token,
    "channel_id": channel_id})

    """DM and message functions are not working. Uncomment when merge"""
    # Sending channel message as user 2.
    response = requests.post(f"{URL}/message/send/v1", json = {"token": user2_token,
    "channel_id": channel_id, "message": "It's 8 clock in the morning🎵🎵🎵"})

    # Creating dm with user 1 and 2. user 2 is dm owner.
    response = requests.post(f"{URL}/dm/create/v1", json = {"token": user2_token,
    "u_ids": [user1_id, user3_id]})
    response_data = response.json()
    dm_id = response_data["dm_id"]

    # Sending dm message as user 2.
    response = requests.post(f"{URL}/message/senddm/v1", json = {"token": user2_token,
    "dm_id": dm_id, "message": "But I stand in California with my toes in the sand"})

    # Remove user from seams.
    response = requests.delete(f"{URL}/admin/user/remove/v1", json = {"token": user1_token, "u_id": user2_id})
    assert response.status_code == 200
    response = requests.delete(f"{URL}/admin/user/remove/v1", json = {"token": user1_token, "u_id": user3_id})
    assert response.status_code == 200

    # Checking user is not in list returned by users/all.
    response = requests.get(f"{URL}/users/all/v1", params = {"token": user1_token})
    response_data = response.json()
    for user in response_data["users"]:
        assert user2_id != user["u_id"]
        assert user3_id != user["u_id"]





def test_admin_user_remove_v1_invalid_user():
    '''
    Test for admin_user_remove_v1.
    Invalid user case (u_id does not refer to a valid user).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Attempting to remove invalid user from seams.
    response = requests.delete(f"{URL}/admin/user/remove/v1", json = {"token": user1_token, "u_id": 123})
    assert response.status_code == 400

def test_admin_user_remove_v1_only_global_owner():
    '''
    Test for admin_user_remove_v1.
    Only global owner case (u_id refers to a user who is the only global owner and they are being demoted to a user)
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]
    auth_user1_id = response_data["auth_user_id"]

    # Attempting to remove only global owner from seams.
    response = requests.delete(f"{URL}/admin/user/remove/v1", json = {"token": user1_token, "u_id": auth_user1_id})
    assert response.status_code == 400

def test_admin_user_remove_v1_unauthorised_user():
    '''
    Test for admin_user_remove_v1.
    Unauthorised access case (the authorised user is not a global owner)
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_id = response_data["auth_user_id"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Attempting to remove user from seams as an unauthorised user.
    response = requests.delete(f"{URL}/admin/user/remove/v1", json = {"token": user2_token, "u_id": user1_id})
    assert response.status_code == 403


"""
Tests for admin_userpermission_change_v1.
"""


def test_admin_userpermission_change_v1_valid_makeowner():
    '''
    Test for admin_userpermission_change_v1.
    Valid case 1 (authorised global owner making a valid user an owner).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_id = response_data["auth_user_id"]

    # Making user 2 an owner.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 1})
    assert response.status_code == 200

def test_admin_userpermission_change_v1_valid_makemember():
    '''
    Test for admin_userpermission_change_v1.
    Valid case 2 (authorised global owner making a valid user a member).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_id = response_data["auth_user_id"]
    user1_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_id = response_data["auth_user_id"]
    user2_token = response_data["token"]

    # Making user 2 an owner as user 1.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 1})

    # Making user 1 a member as user 2.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user2_token, "u_id": user1_id,
    "permission_id": 2})
    assert response.status_code == 200

def test_admin_userpermission_change_v1_invalid_invalidUser():
    '''
    Test for admin_userpermission_change_v1.
    Invalid user case (u_id does not refer to a valid user)
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Attempting to make an invalid user an owner as user 1.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": 12345,
    "permission_id": 1})
    assert response.status_code == 400

def test_admin_userpermission_change_v1_invalid_onlyGlobalOwner():
    '''
    Test for admin_userpermission_change_v1.
    Only global owner case (u_id refers to a user who is the only global owner and they are being demoted to a user).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_id = response_data["auth_user_id"]
    user1_token = response_data["token"]

    # Attempting to make the only global owner a member.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user1_id,
    "permission_id": 2})
    assert response.status_code == 400

def test_admin_userpermission_change_v1_invalid_invalidPermissionID():
    '''
    Test for admin_userpermission_change_v1.
    Invalid permission id case (permission_id is invalid).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_id = response_data["auth_user_id"]

    # Attempting to assign a invalid permission ID to user 2 as user 1.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 5})
    assert response.status_code == 400

def test_admin_userpermission_change_v1_invalid_alreadyIsMember():
    '''
    Test for admin_userpermission_change_v1.
    User already member case (member permissions are given to a user who already has member permissions.)
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_id = response_data["auth_user_id"]

    # Attempting to assign user 2 with a permission ID they already have.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 2})
    assert response.status_code == 400

def test_admin_userpermission_change_v1_invalid_alreadyIsOwner():
    '''
    Test for admin_userpermission_change_v1.
    User already member case (owner permissions are given to a user who already has owner permissions.)
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_id = response_data["auth_user_id"]

    # Making user 2 an owner as user 1.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 1})

    # Attempting to make user 2 an owner again as user 1.
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user1_token, "u_id": user2_id,
    "permission_id": 1})
    assert response.status_code == 400

def test_admin_userpermission_change_v1_invalid_unauthorisedUser():
    '''
    Test for admin_userpermission_change_v1.
    Unauthorised access case (the authorised user is not a global owner).
    '''
    requests.delete(f"{URL}/clear/v1")

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_id = response_data["auth_user_id"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Attempting to make user 1 a member a user 2 (who is unauthorised).
    response = requests.post(f"{URL}/admin/userpermission/change/v1", json = {"token": user2_token, "u_id": user1_id,
    "permission_id": 1})
    assert response.status_code == 403
