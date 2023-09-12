''' Tests for auth.py
Written 25/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au)
for COMP1531 Major Project '''

import pytest

from src.error import InputError, AccessError
from src import config
import requests

# JWT ALGORITHM HS256
# SECRET COMP1531

URL = f'http://localhost:{config.port}'

# Tests for auth_register_v2.

@pytest.fixture()
def clear():
    requests.delete(f'{URL}/clear/v1')


def test_auth_register_v2_valid(clear):
    ''' Registering a valid user '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFyeWFuYm" +
    "FoaW5pcGF0aTFAeWFob28uY29tIiwic2Vzc2lvbl9pZCI6MH0.Y7uNe_2ogFUhVSRe9hvN3xWJzwx" +
    "_4gVxKSnjO4TEpZg", "auth_user_id": 1}
    
def test_auth_register_v2_invalid_email(clear):
    ''' Passing an invalid email '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryan", "password": "123456",
    "name_first": "Aryan", "name_last": "Bahinipati"})

    assert(response.status_code == 400)

def test_auth_register_v2_used_email(clear):
    ''' Trying to register with a used email '''

    requests.post(f'{URL}/auth/register/v2', json = {"email": "aryan@yahoo.com", "password": "123456",
    "name_first": "Aryan", "name_last": "Bahinipati"})

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryan@yahoo.com", "password": "123456",
    "name_first": "Aryan", "name_last": "Bahinipati"})

    assert(response.status_code == 400)

def test_auth_register_v2_invalid_password_length(clear):
    ''' Registering with invalid password length '''


    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "12345", "name_first": "Aryan", "name_last": "Bahinipati"})

    assert(response.status_code == 400)

def test_auth_register_v2_invalid_first_name_length(clear):
    ''' Registering with invalid first name length '''


    response = requests.post(f'{URL}/auth/register/v2', json = {'email': "aryanbahinipati1@yahoo.com",
    'password': "123456", 'name_first': "", 'name_last': "Bahinipati"})

    assert(response.status_code == 400)

def test_auth_register_v2_invalid_last_name_length(clear):
    ''' Registering with invalid last name length '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": ""})

    assert(response.status_code == 400)

# Tests for auth_login_v2.

def test_auth_login_v2_valid(clear):
    ''' Login on valid user '''

    requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    requests.post(f'{URL}/auth/register/v2', json = {"email": "aryan@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response = requests.post(f'{URL}/auth/login/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456"})
    response_data = response.json()
    
    assert(response.status_code == 200)

    assert response_data == {"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFyeWFuYmFoaW5pcG" +
    "F0aTFAeWFob28uY29tIiwic2Vzc2lvbl9pZCI6Mn0._HeqiGp_7TWjI1IOLfDcKVCgp0wAcfV7GOtILc4EirM", "auth_user_id": 1}

def test_auth_login_v2_non_existent_email(clear):
    ''' Login on with non-existent email '''


    response = requests.post(f'{URL}/auth/login/v2', json = {"email": "bob@yahoo.com",
    "password": "123456"})

    assert(response.status_code == 400)

def test_auth_login_v2_incorrect_password(clear):
    ''' Login on with incorrect password email '''

    requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response = requests.post(f'{URL}/auth/login/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "1234567"})

    assert(response.status_code == 400)

def test_auth_logout_v1_invalid_token(clear):
    ''' Passing an invalid token '''

    response = requests.post(f'{URL}/auth/logout/v1', json = {"token": "1234"})

    assert(response.status_code == 403)

def test_auth_logout_v1_valid(clear):
    ''' Valid logout test case user can no longer list channels as token is invalid '''

    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "aryanbahinipati1@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    requests.post(f'{URL}/auth/register/v2', json = {"email": "aryan@yahoo.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    response_data = response.json()

    token = response_data['token']

    response = requests.post(f'{URL}/auth/logout/v1', json = {"token": token})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {}

    response = requests.get(f'{URL}/channels/list/v2', json = {"token": token})

    assert(response.status_code == 403)

def test_auth_passwordreset_request_v1_valid(clear):
    ''' Passes a valid email '''
    
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "arubahi5000@gmail.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    
    response = requests.post(f'{URL}/auth/passwordreset/request/v1', json = {"email": "arubahi5000@gmail.com"})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {}

def test_auth_passwordreset_request_v1_invalid(clear):
    response = requests.post(f'{URL}/auth/passwordreset/request/v1', json = {"email": "aryanbahinipati1@yahoo.com"})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {}

def test_auth_passwordreset_reset_v1_valid(clear):
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "arubahi5000@gmail.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    
    response = requests.post(f'{URL}/auth/passwordreset/request/v1', json = {"email": "arubahi5000@gmail.com"})
    response = requests.post(f'{URL}/auth/passwordreset/reset/v1', json = {"reset_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" +
    ".eyJlbWFpbCI6ImFydWJhaGk1MDAwQGdtYWlsLmNvbSIsInJlc2V0X2NvZGVfaWQiOjF9.CxtuBFd9jpZ4BLDx3gvopI5CUZWmbuP6CaF5Wm1q6oU", 
    "new_password": "12345678"})
    response_data = response.json()

    assert(response.status_code == 200)
    assert response_data == {}
    
    response = requests.post(f'{URL}/auth/login/v2', json = {"email": "arubahi5000@gmail.com", 
    "password": "12345678"})
    
    assert(response.status_code == 200)

def test_auth_passwordreset_reset_v1_invalid_reset_code(clear):
    response = requests.post(f'{URL}/auth/passwordreset/reset/v1', json = {"reset_code": "1234", 
    "new_password": "12345678"})
    
    assert(response.status_code == 400)

def test_auth_passwordreset_reset_v1_invalid_password_length(clear):
    response = requests.post(f'{URL}/auth/register/v2', json = {"email": "arubahi5000@gmail.com",
    "password": "123456", "name_first": "Aryan", "name_last": "Bahinipati"})
    
    response = requests.post(f'{URL}/auth/passwordreset/request/v1', json = {"email": "arubahi5000@gmail.com"})
    response = requests.post(f'{URL}/auth/passwordreset/reset/v1', json = {"reset_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" + 
    ".eyJlbWFpbCI6ImFydWJhaGk1MDAwQGdtYWlsLmNvbSIsInJlc2V0X2NvZGVfaWQiOjF9.CxtuBFd9jpZ4BLDx3gvopI5CUZWmbuP6CaF5Wm1q6oU", 
    "new_password": "1234"})
    
    assert(response.status_code == 400)

