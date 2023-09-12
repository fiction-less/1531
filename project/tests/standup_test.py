''' Tests for dm.py
Written 13/04/22
by Ding Mingrui (z5292268@ad.unsw.edu.au)
for COMP1531 Major Project '''
import time

import pytest
from flask import request
from src.error import InputError, AccessError
from src import config
import requests

# JWT ALGORITHM HS256
# SECRET COMP1531
URL = f'http://localhost:{config.port}'
def test_standup_start_in_token():
    requests.delete(f'{URL}/clear/v1')
    chan_resp = requests.post(f'{URL}/standup/start/v1', json={
        "token": "1234",
        "channel_id": 1,
        "length": 10})
    assert (chan_resp.status_code == 403)
def test_standup_start_not_in_channel_id():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    chan_resp = requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": 10})
    assert (chan_resp.status_code == 400)
def test_standup_start_neg_length():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    chan_resp = requests.post(f'{URL}/channels/create/v2', json={
        "token": token,
        "name": "HaydensChannel",
        "is_public": True})

    chan_resp = requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": -1})
    assert (chan_resp.status_code == 400)
def test_standup_start_running():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    requests.post(f'{URL}/channels/create/v2', json={
        "token": token,
        "name": "HaydensChannel",
        "is_public": True})
    chan_resp = requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": 100})
    chan_resp.json()
    assert (chan_resp.status_code == 200)
    chan_resp1 = requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": 1})
    assert (chan_resp1.status_code == 400)
def test_standup_start_not_a_member():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "midsdsng1@yahoo.com",
                                                              "password": "123456", "name_first": "dsdui",
                                                              "name_last": "sdsg"})
    response_data = response.json()
    token1 = response_data['token']
    requests.post(f'{URL}/channels/create/v2', json={
        "token": token,
        "name": "HaydensChannel",
        "is_public": True})
    chan_resp = requests.post(f'{URL}/standup/start/v1', json={
        "token": token1,
        "channel_id": 1,
        "length": 100})
    assert (chan_resp.status_code == 403)
def test_standup_active_in_token():
    requests.delete(f'{URL}/clear/v1')
    payload = {"token": "1234", 'channel_id': 1}
    a = requests.get(f'{URL}/standup/active/v1', params=payload)
    assert(a.status_code == 403)
def test_standup_active_not_in():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    payload = {"token": token, 'channel_id': 1}
    a = requests.get(f'{URL}/standup/active/v1', params=payload)
    assert(a.status_code == 400)
def test_standup_active_not_a_member():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "midsdsng1@yahoo.com",
                                                              "password": "123456", "name_first": "dsdui",
                                                              "name_last": "sdsg"})
    response_data = response.json()
    token1 = response_data['token']
    requests.post(f'{URL}/channels/create/v2', json={
        "token": token,
        "name": "HaydensChannel",
        "is_public": True})
    payload = {"token": token1, 'channel_id': 1}
    a = requests.get(f'{URL}/standup/active/v1', params=payload)
    assert (a.status_code == 403)
    payload = {"token": token, 'channel_id': 1}
    b = requests.get(f'{URL}/standup/active/v1', params=payload)
    assert (b.status_code == 200)
    requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": 20})
    payload = {"token": token, 'channel_id': 1}
    c = requests.get(f'{URL}/standup/active/v1', params=payload)
    assert (c.status_code == 200)
def test_standup_send_in_token():
    requests.delete(f'{URL}/clear/v1')
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": "1234",
        "channel_id": 1,
        "message": "hello"})
    assert (chan_resp.status_code == 403)
def test_standup_send_not_in_channel_id():
    requests.delete(f'{URL}/clear/v1')
    we = requests.post(f'{URL}/auth/register/v2', json={"email": "aryanbahinipati1@yahoo.com",
                                                        "password": "123456", "name_first": "Aryan",
                                                        "name_last": "Bahinipati"})
    response_data = we.json()
    token = response_data['token']
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token,
        "channel_id": 1,
        "message": "hello"})
    assert (chan_resp.status_code == 400)
    response = requests.post(f'{URL}/auth/register/v2', json={"email": "midsdsng1@yahoo.com",
                                                              "password": "123456", "name_first": "dsdui",
                                                              "name_last": "sdsg"})
    response_data = response.json()
    token1 = response_data['token']
    requests.post(f'{URL}/channels/create/v2', json={
        "token": token,
        "name": "HaydensChannel",
        "is_public": True})
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token1,
        "channel_id": 1,
        "message": "hello"})
    assert (chan_resp.status_code == 403)
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token,
        "channel_id": 1,
        "message": "hello"})
    assert (chan_resp.status_code == 400)
    requests.post(f'{URL}/standup/start/v1', json={
        "token": token,
        "channel_id": 1,
        "length": 20})
    mess = "i"*1002
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token,
        "channel_id": 1,
        "message": mess})
    assert (chan_resp.status_code == 400)
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token,
        "channel_id": 1,
        "message": "hello"})
    chan_resp = requests.post(f'{URL}/standup/send/v1', json={
        "token": token,
        "channel_id": 1,
        "message": "hello"})
    time.sleep(20)

