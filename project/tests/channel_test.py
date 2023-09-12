''' Tests for channel.py
Written 26/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au), Daniel Wang (z5312741@ad.unsw.edu.au) and Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

from flask import request
from src.error import AccessError, InputError
from src import config
import requests

URL = f'http://localhost:{config.port}'

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')

'''
Tests for channel_join_v2.
'''

def test_channel_join_v2_invalid_channel(clear):
    ''' Trying to join with invalid channel id '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token,
    "channel_id": 10000})

    assert(response.status_code == 400)

def test_channel_join_v2_already_member_invalid(clear):
    ''' Trying to join with a member that is already part of channel '''


    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token,
    "channel_id": channel_id})

    assert(response.status_code == 400)

def test_channel_join_v2_private_channel_invalid(clear):
    ''' Trying to join private channel when youre not global owner'''


    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token_1 = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "bob@yahoo.com",
    "password": "123456", "name_first": "Bob", "name_last": "Smith"})
    response_data = response.json()

    token_2 = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token_1,
    "name": "Channel1", "is_public": False})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token_2,
    "channel_id": channel_id})

    assert(response.status_code == 403)

def test_channel_join_v2_private_channel_valid(clear):
    ''' Trying to join private channel when youre global owner'''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token_1 = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "bob@yahoo.com",
    "password": "123456", "name_first": "Bob", "name_last": "Smith"})
    response_data = response.json()

    token_2 = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token_2,
    "name": "Channel1", "is_public": False})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token_1,
    "channel_id": channel_id})

    assert(response.status_code == 200)


def test_channel_join_v2_invalid_token(clear):
    ''' Trying to join channel with an invalid token '''


    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": "1234",
    "channel_id": channel_id})

    assert(response.status_code == 403)

def test_channel_join_v2_valid(clear):
    ''' Trying to join channel valid test case '''
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token_1 = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "bob@yahoo.com",
    "password": "123456", "name_first": "Bob", "name_last": "Smith"})
    response_data = response.json()

    token_2 = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token_1,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token_2,
    "channel_id": channel_id})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {}




'''
Tests for channel_leave_v1
'''



def test_channel_leave_v1_valid_twoChannelOwners(clear):
    '''
    Test for channel/leave/v1. Valid case: authorised user is a member of the channel.
    '''

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()

    # Creating channel with user 1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # User 1 leaves channel.
    response = requests.post(f"{URL}/channel/leave/v1", json = {"token": user_token,
    "channel_id": channel_id})
    response_data = response.json()

    assert response.status_code == 200
    assert response_data == {}

def test_channel_leave_v1_invalid_channel(clear):
    '''
    Test for channel/leave/v1. Invalid channel case.
    '''

    # Registering user.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Leaving user from invalid channel.
    response = requests.post(f"{URL}/channel/leave/v1", json = {"token": user_token,
    "channel_id": 100})
    assert response.status_code == 400

def test_channel_leave_v1_invalid_member(clear):
    '''
    Test for channel/leave/v1. Invalid member case.
    '''

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Leaving user 2 (invalid member) from channel
    response = requests.post(f"{URL}/channel/leave/v1", json = {"token": user2_token,
    "channel_id": channel_id})
    assert response.status_code == 403



'''
Tests for channel/addowner/v1
'''


def test_channel_addowner_v1_valid(clear):
    '''
    Test for test_channel_addowner_v1.
    Valid case (authorised user with token 'token' has priveledges to add user with ID 'u_id' as an owner to a channel with ID 'channel_id').
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]
    auth_user2_id = response_data["auth_user_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Adding user 2 as owner.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})
    assert response.status_code == 200

def test_channel_addowner_v1_invalid_channel(clear):
    '''
    Test for channel_addowner_v1.
    Invalid channel case (channel_id does not refer to a valid channel).
    '''

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    auth_user2_id = response_data["auth_user_id"]

    # Attempting to add user 1 to an invalid channel.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": 100, "u_id": auth_user2_id})
    assert response.status_code == 400

def test_channel_addowner_v1_invalid_user(clear):
    '''
    Test for channel_addowner_v1.
    Invalid user case (u_id does not refer to a valid user).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Attempting to add invalid user.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": 12345})
    assert response.status_code == 400

def test_channel_addowner_v1_user_id_owner_not_member(clear):
    '''
    Test for channel_addowner_v1.
    Invalid member case (u_id does not refer to a user who is a member of the channel).
    '''

    # Registering user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Registering user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    auth_user2_id = response_data["auth_user_id"]

    # Attempting to add user 2 (who is not a member of the channel) as an owner.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})
    assert response.status_code == 400

def test_channel_addowner_v1_already_owner(clear):
    '''
    Test for channel_addowner_v1.
    Already owner case (u_id refers to au ser who is already an owner of the channel).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]
    auth_user2_id = response_data["auth_user_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Adding user 2 as owner.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})

    # Attempting to add user 2 as owner again.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})
    assert response.status_code == 400

def test_channel_addowner_v1_unauthorised_access(clear):
    '''
    Test for channel_addowner_v1.
    Unauthorised user case (channel_id is valid and authorised user is not an owner).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    user3_token = response_data["token"]
    auth_user3_id = response_data["auth_user_id"]

    # Joining user 3 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user3_token,
    "channel_id": channel_id})

    # Attempting to add user 3 as owner when user 2 is not an owner.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user2_token,
    "channel_id": channel_id, "u_id": auth_user3_id})
    assert response.status_code == 403

def test_channel_addowner_v1_global_owner_can_addowner(clear):
    """
    Test for channel_addowner_v1.
    Case: Global owner who is not a channel owner can addowner.
    """
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

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    user3_token = response_data["token"]
    auth_user3_id = response_data["auth_user_id"]

    # Creating channel with user 2 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 1 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user_token,
    "channel_id": channel_id})

    # Joining user 3 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user3_token,
    "channel_id": channel_id})

    # Giving user 3 owner permissions as global owner user 1.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user3_id})
    assert response.status_code == 200

def test_channel_addowner_v1_non_member(clear):
    """
    Test for channel_addowner_v1.
    Case: Non member cannot addowner.
    """
    # Register global owner user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]
    auth_user_id = response_data["auth_user_id"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    user3_token = response_data["token"]

    # Creating channel with user 2 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 1 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user_token,
    "channel_id": channel_id})

    # Attempting to join user 1 to channel as non member user 3.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user3_token,
    "channel_id": channel_id, "u_id": auth_user_id})
    assert response.status_code == 403

def test_channel_addowner_v1_global_owner_non_member_public(clear):
    """
    Test for channel_addowner_v1.
    Case: Global owner who is not a member cannot addowner to a public channel.
    """
    # Register global owner user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    user3_token = response_data["token"]
    auth_user3_id = response_data["auth_user_id"]

    # Creating channel with user 2 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 3 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user3_token,
    "channel_id": channel_id})

    # Attempting to add user 3 as channel owner when global owner user 1 is not a member.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user3_id})
    assert response.status_code == 403

def test_channel_addowner_v1_global_owner_non_member_private(clear):
    """
    Test for channel_addowner_v1.
    Case: Global owner who is not a member cannot addowner to a private channel.
    """
    # Register global owner user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Register user 3.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "lewis@gmail.com",
    "password": "f1goat", "name_first": "lewis", "name_last": "hamilton"})
    response_data = response.json()
    auth_user3_id = response_data["auth_user_id"]

    # Creating channel with user 2 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": False})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 3 to channel.
    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": user2_token,
    "channel_id": channel_id, "u_id": auth_user3_id})

    # Attempting to add user 3 as channel owner when global owner user 1 is not a member.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user3_id})
    assert response.status_code == 403

def test_channel_addowner_v1_invalid_token(clear):
    """
    Test for channel_addowner_v1.
    Case: Invalid token cannot addowner.
    """
    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    auth_user_id = response_data["auth_user_id"]
    user_token = response_data["token"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]

    # Creating channel with user 2 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 1 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user_token,
    "channel_id": channel_id})

    # Attempting to add user 1 as owner with an invalid token.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": "banana123",
    "channel_id": channel_id, "u_id": auth_user_id})
    assert response.status_code == 403
'''
Tests for channel/removeowner/v1.
'''

def test_channel_removeowner_v1_valid(clear):
    '''
    Test for channel_remove_owner_v1.
    Valid case (authorised user with token 'token' has priveledges to remove user with ID 'u_id' as an owner of the channel with ID 'channel_id)
    '''


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
    auth_user2_id = response_data["auth_user_id"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Adding user 2 as owner.
    response = requests.post(f"{URL}/channel/addowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})

    # Removing user 2 as owner.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})
    assert response.status_code == 200


def test_channel_removeowner_v1_invalid_channel(clear):
    '''
    Test for channel_remove_owner_v1.
    Invalid channel case (channel_id does not refer to a valid channel).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    auth_user2_id = response_data["auth_user_id"]

    # Removing user 2 as owner from an invalid channel.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token,
    "channel_id": 100, "u_id": auth_user2_id})
    assert response.status_code == 400

def test_channel_removeowner_v1_invalid_user(clear):
    '''
    Test for channel_remove_owner_v1.
    Invalid user case (u_id does not refer to a valid user).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Removing invalid user as owner.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": 12345})
    assert response.status_code == 400

def test_channel_removeowner_v1_user_not_owner(clear):
    '''
    Test for channel_removeowner_v1.
    Invalid owner case (u_id refers to a user who is not an owner of the channel).
    '''

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
    auth_user2_id = response_data["auth_user_id"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user2_token,
    "channel_id": channel_id})

    # Attempting to remove user 2 as owner.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user2_id})
    assert response.status_code == 400

def test_channel_removeowner_v1_user_only_owner(clear):
    '''
    Test for channel_removeowner_v1.
    Only owner case (u_id refers to a user who is currently the onyl owner of the channel).
    '''

    # Register user 1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]
    auth_user_id = response_data["auth_user_id"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

    # Attempting to remove user 1 (who is the only owner) as owner.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token,
    "channel_id": channel_id, "u_id": auth_user_id})
    assert response.status_code == 400


def test_channel_removeowner_v1_unauthorised_user(clear):
    '''
    Test for channel_removeowner_v1.
    Unauthorised user case (channel_id is valid and authorised user does not have owner permissions).
    '''

    # Register user 1/ seams with owner permissions
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user_token = response_data["token"]
    auth_user_id = response_data["auth_user_id"]


    # Register user 2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user_token1 = response_data["token"]

    # Creating channel with user 1 as owner.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    channel_id = response_data["channel_id"]

     # Joining user 2 to channel.
    response = requests.post(f'{URL}/channel/join/v2', json = {"token": user_token1,
    "channel_id": channel_id})

    # User 2 attempting to remove user 1 with no owner permissions
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user_token1,
    "channel_id": channel_id, "u_id": auth_user_id})
    assert response.status_code == 403

def test_channel_removeowner_v1_global_owner_nonmember(clear):
    """
    Test for channel_removeowner_v1.
    Case: Global owner who is not a member cannot remove owner from channel.
    """

    # Register global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]

    # Register user2.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "tracy@gmail.com",
    "password": "roasted&salted", "name_first": "tracy", "name_last": "yap"})
    response_data = response.json()
    user2_token = response_data["token"]
    u2_id = response_data["auth_user_id"]

    # Creating channel with owner user2.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user2_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Attempting to remove user2 as owner from channel as non-member user1.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": user1_token,
    "channel_id": ch_id, "u_id": u2_id})
    assert response.status_code == 403

def test_channel_removeowner_v1_invalid_token(clear):
    """
    Test for channel_removeowner_v1.
    Case: Invalid token.
    """
    # Register global owner user1.
    response = requests.post(f"{URL}/auth/register/v2", json = {"email": "dan@gmail.com",
    "password": "freedom", "name_first": "dan", "name_last": "wang"})
    response_data = response.json()
    user1_token = response_data["token"]
    u1_id  = response_data["auth_user_id"]

    # Creating channel with owner user1.
    response = requests.post(f"{URL}/channels/create/v2", json = {"token": user1_token,
    "name": "channel1", "is_public": True})
    response_data = response.json()
    ch_id = response_data["channel_id"]

    # Attempting to remove user1 as owner from channel with invalid token.
    response = requests.post(f"{URL}/channel/removeowner/v1", json = {"token": "Invalid Token",
    "channel_id": ch_id, "u_id": u1_id})
    assert response.status_code == 403
'''
tests for channel invite
'''

def test_channel_invite_v1_invalid_token(clear):
    '''invalid token'''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "yo@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    uid1 = response_data['auth_user_id']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": "invalidtoken",
    "channel_id": channel_id, "u_id": uid1})

    assert response.status_code == 403


def test_channel_invite_v1_invalid_channel(clear):
    '''channel is invalid'''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aradfhakshkfj@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()
    print(response_data)
    uid2 = response_data['auth_user_id']

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": token,
    "channel_id": 10000, "u_id": uid2})

    assert response.status_code == 400


def test_channel_invite_v1_invalid_user(clear):
    '''the user being invited is invalid'''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": token,
    "channel_id": channel_id, "u_id": 2})

    assert response.status_code == 400


def test_channel_invite_v1_already_member_invalid(clear):
    '''the user being invited is already a member'''
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "yo@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token1 = response_data['token']
    uid1 = response_data['auth_user_id']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token1,
    "channel_id": channel_id})

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": token,
    "channel_id": channel_id, "u_id": uid1})

    assert response.status_code == 400


def test_channel_invite_v1_invitation_from_non_channel_member(clear):
    '''the user inviting is not part of the channel'''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "hayeden@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token2 = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "yoooo@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    uid3 = response_data['auth_user_id']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": token2,
    "channel_id": channel_id, "u_id": uid3})

    assert response.status_code == 403

def test_channel_invite_v1_valid(clear):

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "yo@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    uid1 = response_data['auth_user_id']

    response = requests.post(f'{URL}/channels/create/v2', json = {"token": token,
    "name": "Channel1", "is_public": True})
    response_data = response.json()

    channel_id = response_data['channel_id']

    response = requests.post(f'{URL}/channel/invite/v2', json = {"token": token,
    "channel_id": channel_id, "u_id": uid1})

    assert response.status_code == 200
    assert response.json() == {}


'''
Channel details tests
'''

def test_channel_details_v1_valid_multiple_members(clear):
    ''' Passes a valid channel details request '''

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token_1 = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {"token": token_1, "name": "Channel1",
    "is_public": True})

    channel = chan_resp.json()
    channel_id = channel['channel_id']
    print(channel_id)

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "bob.ross@gmail.com",
    "password": "testing2", "name_first": "Bob", "name_last": "Ross"})

    user = user_resp.json()
    token_2 = user['token']

    response = requests.post(f'{URL}/channel/join/v2', json = {"token": token_2, "channel_id": channel_id})

    payload = {"token": token_2, "channel_id": channel_id}

    response = requests.get(f'{URL}/channel/details/v2', params = payload)
    response_data = response.json()
    print(response_data)

    assert(response.status_code == 200)
    assert response_data == {
        'name': 'Channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'alyssa.lubrano1@gmail.com',
                'name_first': 'Alyssa',
                'name_last': 'Lubrano',
                'handle_str': 'alyssalubrano',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'alyssa.lubrano1@gmail.com',
                'name_first': 'Alyssa',
                'name_last': 'Lubrano',
                'handle_str': 'alyssalubrano',
            },
            {
                'u_id': 2,
                'email': 'bob.ross@gmail.com',
                'name_first': 'Bob',
                'name_last': 'Ross',
                'handle_str': 'bobross',
            }
        ]
    }

def test_channel_details_invalid_token(clear):
    invalid_token = "hihihihh"
    payload = {'token': invalid_token, 'channel_id': -1}

    response = requests.get(f'{URL}/channel/details/v2', params = payload)
    assert(response.status_code == 403)


def test_channel_details_v1_invalid_channel_id(clear):

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    response_data = response.json()
    token = response_data['token']

    payload = {'token': token, 'channel_id': -1}

    response = requests.get(f'{URL}/channel/details/v2', params = payload)
    assert(response.status_code == 400)


def test_channel_details_v1_invalid_not_member_of_channel(clear):

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "alyssa.lubrano1@gmail.com",
    "password": "testing", "name_first": "Alyssa", "name_last": "Lubrano"})

    user = user_resp.json()
    token_1 = user['token']

    user_resp = requests.post(f'{URL}/auth/register/v2', json = {"email": "bob.ross@gmail.com",
    "password": "testing2", "name_first": "Bob", "name_last": "Ross"})

    user = user_resp.json()
    token_2 = user['token']

    chan_resp = requests.post(f'{URL}/channels/create/v2', json = {"token": token_2, "name": "BobsChannel",
    "is_public": False})
    channel = chan_resp.json()
    channel_id = channel['channel_id']

    payload = {'token': token_1, 'channel_id': channel_id}
    response = requests.get(f'{URL}/channel/details/v2', params = payload)
    assert(response.status_code == 403)
