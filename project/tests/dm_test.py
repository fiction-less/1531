''' Tests for dm.py
Written 18/03/22
by Ding Mingrui (z5292268@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest
from flask import request
from src.error import InputError, AccessError
from src import config
import requests

# JWT ALGORITHM HS256
# SECRET COMP1531
URL = f'http://localhost:{config.port}'
''' Tests for dm.py
Written 18/03/22
by Ding Mingrui (z5292268@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest
from flask import request
from src.error import InputError, AccessError
from src import config
import requests

# JWT ALGORITHM HS256
# SECRET COMP1531
URL = f'http://localhost:{config.port}'
def test_dm_create_v1__u_id():
    ''' duplicate_u_id '''

    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = we.json()

    token5 = response_data['token']
    member2 = requests.post(f'{URL}/auth/register/v2', json={"email": "mingruiding1@yahoo.com",
                                                              "password": "123456", "name_first": "mingrui",
                                                              "name_last": "ding"})
    response_data = member2.json()

    token2 = response_data['token']
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "midsdsng1@yahoo.com",
                                                              "password": "123456", "name_first": "dsdui",
                                                              "name_last": "sdsg"})
    response_data = response.json()

    token = response_data['token']

    response1 = requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": [1, 2]})
    response_data = response1.json()
    assert response_data == {'dm_id': 1}
    response2 = requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": [1]})
    response_data = response2.json()
    assert response_data == {'dm_id': 2}
    response3 = requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": [2]})
    response_data = response3.json()
    assert response_data == {'dm_id': 3}
    assert (response.status_code == 200)
    for i in range(0, 5):
        requests.post(f"{URL}/message/senddm/v1", json={
            'token': token,
            'dm_id': 1,
            'message': f"{i}time to learn"
        })
    payload = {"token": token, 'dm_id': 1, 'start': 1}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)
    for i in range(0, 60):
        requests.post(f"{URL}/message/senddm/v1", json={
            'token': token,
            'dm_id': 1,
            'message': f"{i}time to learn"
        })
    payload = {"token": token, 'dm_id': 1, 'start': 1}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)
    payload = {"token": token}
    a = requests.get(f'{URL}/dm/list/v1', params=payload)
    response_data = a.json()
    assert response_data == {'dms': [{'dm_id': 1, 'name': 'aryanbahinipati, dsduisdsg, mingruiding'},
                                     {'dm_id': 2, 'name': 'aryanbahinipati, dsduisdsg'},
                                     {'dm_id': 3, 'name': 'dsduisdsg, mingruiding'}]}
    payload1 = {"token": token, 'dm_id': 1}
    asd = requests.get(f'{URL}/dm/details/v1', params=payload1)
    response_data = asd.json()
    assert response_data == {'name': 'aryanbahinipati, dsduisdsg, mingruiding',
                            'members': [{'u_id': 1,
                                            'email': 'aryanbahinipati1@yahoo.com',
                                            'handle_str': 'aryanbahinipati',
                                            'name_first': 'Aryan',
                                            'name_last': 'Bahinipati'
                                            },
                                           {'u_id': 2,
                                            'email': 'mingruiding1@yahoo.com',
                                            'handle_str': 'mingruiding',
                                            'name_first': 'mingrui',
                                            'name_last': 'ding'
                                            },
                                           {'u_id': 3,
                                            'email': 'midsdsng1@yahoo.com',
                                            'handle_str': 'dsduisdsg',
                                            'name_first': 'dsdui',
                                            'name_last': 'sdsg'
                                            }]}
    requests.delete(f"{URL}/dm/remove/v1", json={
        'token': token,
        'dm_id': 2,
    })
    payload = {"token": token}
    a = requests.get(f'{URL}/dm/list/v1', params=payload)
    response_data = a.json()
    assert response_data == {'dms': [{'dm_id': 1, 'name': 'aryanbahinipati, dsduisdsg, mingruiding'},
                                     {'dm_id': 3, 'name': 'dsduisdsg, mingruiding'}]}
    requests.post(f'{URL}/dm/leave/v1', json={"token": token5, "dm_id": 1})
    payload1 = {"token": token5, 'dm_id': 1}
    asd = requests.get(f'{URL}/dm/details/v1', params=payload1)
    response_data = asd.json()
    assert response_data == {'name': 'aryanbahinipati, dsduisdsg, mingruiding',
                             'members': [{'u_id': 2,
                                             'email': 'mingruiding1@yahoo.com',
                                             'handle_str': 'mingruiding',
                                             'name_first': 'mingrui',
                                             'name_last': 'ding'
                                             },
                                            {'u_id': 3,
                                             'email': 'midsdsng1@yahoo.com',
                                             'handle_str': 'dsduisdsg',
                                             'name_first': 'dsdui',
                                             'name_last': 'sdsg'
                                             }]}
    '''assert response_data == {}'''
    assert (response.status_code == 200)
    requests.post(f'{URL}/dm/leave/v1', json={"token": token, "dm_id": 3})
    payload2 = {"token": token2, 'dm_id': 3}
    asds = requests.get(f'{URL}/dm/details/v1', params=payload2)
    response_data = asds.json()
    assert response_data == {'name': 'dsduisdsg, mingruiding',
                             'members': [{'u_id': 2,
                                             'email': 'mingruiding1@yahoo.com',
                                             'handle_str': 'mingruiding',
                                             'name_first': 'mingrui',
                                             'name_last': 'ding'
                                             }]}
def test_dm_create_v1_duplicate_u_id():
    ''' duplicate_u_id '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": [2, 2, 3, 4, 5]})
    assert (response.status_code == 400)
def test_dm_create_v2_invalid_token():
    ''' Passes an invalid token '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/dm/create/v1', json={"token": "1234", "u_ids": [2, 3, 4, 5]})
    assert (response.status_code == 403)
def test_dm_create_v2_invalid_u_id():
    ''' Channel name is bigger than 20 characters '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": [2]})

    assert (response.status_code == 400)
def test_dm_list_v1_invalid_token():
    ''' Passes an invalid token '''

    requests.delete(f'{URL}/clear/v1')
    payload = {"token": "1234"}
    response = requests.get(f'{URL}/dm/list/v1', params=payload)

    assert (response.status_code == 403)
def test_dm_list_v1_no_dm():

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}
    response = requests.get(f'{URL}/dm/list/v1', params = payload)
    response_data = response.json()
    assert response_data == {'dms': []}
    assert (response.status_code == 200)


def test_dm_list_v1_one_channel():
    ''' Authorised user is part of 1 channels '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token}

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})

    response = requests.get(f'{URL}/dm/list/v1', params=payload)
    response_data = response.json()

    assert (response.status_code == 200)
    assert response_data == {'dms': [{'dm_id': 1, 'name': 'aryanbahinipati'}]}
def test_remove_dm():
    '''in token'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})

    a = requests.delete(f"{URL}/dm/remove/v1", json={
        'token': '1234',
        'dm_id': 2,
    })
    assert(a.status_code == 403)
def test_remove_dm1():
    '''in id'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})

    a = requests.delete(f"{URL}/dm/remove/v1", json={
        'token': token,
        'dm_id': 2,
    })
    assert(a.status_code == 400)
def test_remove_dm2():
    '''not the creater'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "ryanbahinipati1@yahoo.com",
                                                              "password": "1234s56", "name_first": "Adryan",
                                                              "name_last": "Bahinispati"})
    response_data = response.json()

    token = response_data['token']
    a = requests.delete(f"{URL}/dm/remove/v1", json={
        'token': token,
        'dm_id': 1,
    })
    assert (a.status_code == 403)
def test_dm_detail_v1token():
    requests.delete(f'{URL}/clear/v1')
    payload = {"token": "1234", 'dm_id': 2}
    response = requests.get(f'{URL}/dm/details/v1', params=payload)
    assert (response.status_code == 403)
def test_dm_detail_v1():
    ''' Authorised user is part of 1 channels '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token, 'dm_id': 2}

    response = requests.get(f'{URL}/dm/details/v1', params=payload)

    assert (response.status_code == 400)
def test_detail_dm1():
    '''not a member'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()
    token = response_data['token']

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "ryanbahinipati1@yahoo.com",
                                                              "password": "1234s56", "name_first": "Adryan",
                                                              "name_last": "Bahinispati"})
    response_data = response.json()
    token1 = response_data['token']
    payload = {"token": token1, 'dm_id': 1}
    a = requests.get(f"{URL}/dm/details/v1", params=payload)
    assert (a.status_code == 403)

def test_dm_leave_v1_invalid_token():
    ''' Passes an invalid token '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/dm/leave/v1', json={"token": "1234", "dm_id": 1})
    assert (response.status_code == 403)
def test_dm_leave_v1_invalid_token1():
    ''' not a member '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "ryanbahinipati1@yahoo.com",
                                                              "password": "1234s56", "name_first": "Adryan",
                                                              "name_last": "Bahinispati"})
    response_data = response.json()
    token = response_data['token']

    response = requests.post(f'{URL}/dm/leave/v1', json={"token": token, "dm_id": 1})
    assert (response.status_code == 403)
def test_dm_leave_v1_invalid_token2():
    ''' not valid id '''

    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "ryanbahinipati1@yahoo.com",
                                                              "password": "1234s56", "name_first": "Adryan",
                                                              "name_last": "Bahinispati"})
    response_data = response.json()
    token = response_data['token']
    response = requests.post(f'{URL}/dm/leave/v1', json={"token": token, "dm_id": 1})
    assert (response.status_code == 400)
def test_message_dm1():
    '''not a vaild id'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    payload = {"token": token, 'dm_id': 1, 'start': 0}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)

    assert (a.status_code == 400)
def test_message_dm5():
    '''in token'''
    requests.delete(f'{URL}/clear/v1')
    payload = {"token": "1234", 'dm_id': 1, 'start': 0}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)

    assert (a.status_code == 403)
def test_message_dm2():
    '''no message'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    payload = {"token": token, 'dm_id': 1, 'start': 0}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)

    response_data = a.json()

    assert (response.status_code == 200)
    assert response_data == {'messages': [], 'start': 0, 'end': -1}
def test_message_dm22():
    '''start < 0'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    payload = {"token": token, 'dm_id': 1, 'start': -1}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)
    assert (a.status_code == 400)
def test_message_dm3():
    '''not a member'''
    requests.delete(f'{URL}/clear/v1')
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Aryan",
                                                              "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']
    requests.post(f'{URL}/dm/create/v1', json={"token": token, "u_ids": []})
    r1esponse = requests.post(f'{URL}/auth/register/v2', json={"email": "1aryanbahinipati1@yahoo.com",
                                                              "password": "123456", "name_first": "Arryan",
                                                              "name_last": "Brahinipati"})
    response_data = r1esponse.json()

    token = response_data['token']
    payload = {"token": token, 'dm_id': 1, 'start': 1}
    a = requests.get(f'{URL}/dm/messages/v1', params=payload)
    assert (a.status_code == 403)
