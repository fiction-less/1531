''' Implementation of auth functions
Written 25/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au)
or COMP1531 Major Project '''

from src.data_store import data_store
from src.error import InputError, AccessError
from hashlib import sha256
from src.other import get_index
from src import config
from email.message import EmailMessage

import re
import jwt
import smtplib
import urllib.request
import requests

URL = f'http://localhost:{config.port}'

def create_handle(name_first, name_last):
    """
    Helper function for auth_register_v1 to create a handle for a user
    Parameters:
        - name_first (string): users first name
        - name_last (string): users last name
    Exceptions:
        N/A
    Returns:
        handle (string): users new handle.
    """

    store = data_store.get()

    handle = ''.join(c for c in ((name_first + name_last).lower()) if c.isalnum())[0:20]

    for i in range(0, len(store['handle']) + 1):
        if handle not in store['handle']:
            break
        elif (handle + str(i)) not in store['handle']:
            handle = handle + str(i)
            break

    return handle

def valid_email(email):
    """
    Helper function for auth_register_v1_checks to check for valid email.
    Parameters:
        - email (string): email to be checked.
    Exceptions:
        N/A
    Returns:
        bool (true if valid email, false if invalid email)
    """

    if re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        return True
    else:
        return False

def auth_register_v1_checks(email, password, name_first, name_last):
    """
    Helper function for auth_register_v1 to check for errors.
    Parameters: { email, password }
        - email (string): email of registered user.
        - password (string): password of registered user.
        - name_first (string): first name of registered user.
        - name_last (string): last name of registered user.
    Exceptions:
        - email entered is not a valid email
        - email addresss is already being used by another user.
        - length of password is less than 6 characters.
        - length of name_first is not between 1 and 50 characters inclusive.
        - length of name_last is not between 1 and 50 characters inclusvive.
    Returns: If successfully registered returns { token, auth_user_id }
        - token (string): registered users new token.
        - auth_user_id (int): registeed users new user_id.
    """

    store = data_store.get()

    if valid_email(email) == False:
        raise InputError(description = "InputError: Invalid email")
    elif email in store['email']:
        raise InputError(description = "InputError: Email already exists")
    elif len(password) < 6:
        raise InputError(description = "InputError: Password too short")
    elif len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description = "InputError: Length of name_first not between 1-50 characters")
    elif len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description = "InputError: Length of name_last not between 1-50 characters")

def auth_login_v1_checks(email, password):
    """
    Given a registered user's email and password, returns their `auth_user_id` value and a new `token`.
    Parameters: { email, password }
        - email (string): user's email
        - password (string): user's password
    Exceptions:
        - InputError: Occurs when;
            - email does not belong to a user.
            - password incorrect.
    Returns: If user is logged in, returns { token, auth_user_id }
        - token (string): user's new token.
        - auth_user_id (int): user's new ID.
    """

    store = data_store.get()

    if email not in store['email']:
        raise InputError(description = "InputError: Email entered does not belong to user")
    else:
        index = store['email'].index(email)

        if store['password'][index] != sha256(password.encode('utf-8')).hexdigest():
            raise InputError(description = "InputError: Password is not correct")

def auth_login_v1(email, password):
    ''' Given a registered user's email and password, returns their 'auth_user_id' value
        Arguments:
            email (string) - user's email
            password (string) - user's password
        Exceptions:
            InputError - Occurs when:
                - email entered  does not belong to a user
                - password isn't correct
        Return Value:
            Returns {auth_user_id} if no exceptions are raised and 'auth_user_id' is found in the datastore.'''

    store = data_store.get()

    auth_login_v1_checks(email, password)

    index = store['email'].index(email)
    token = jwt.encode({"email": email, "session_id": store['session_id']},
    "COMP1531", algorithm = "HS256")
    store['token'][index].append(token)
    store['session_id'] += 1
    data_store.set(store)

    return {
        "token": token, "auth_user_id": store['user_id'][index]
    }

def auth_register_v1(email, password, name_first, name_last):
    """
    Given a user's first and last name, email address, and password, create a new account for them and return a new `auth_user_id` and `token`.
    Parameters: { email, password }
        - email (string): email of registered user.
        - password (string): password of registered user.
        - name_first (string): first name of registered user.
        - name_last (string): last name of registered user.
    Exceptions:
        - email entered is not a valid email
        - email addresss is already being used by another user.
        - length of password is less than 6 characters.
        - length of name_first is not between 1 and 50 characters inclusive.
        - length of name_last is not between 1 and 50 characters inclusvive.
    Returns: If successfully registered returns { token, auth_user_id }
        - token (string): registered users new token.
        - auth_user_id (int): registeed users new user_id.
    """

    store = data_store.get()

    auth_register_v1_checks(email, password, name_first, name_last)

    encoded_jwt = jwt.encode({"email": email, "session_id": store['session_id']},
    "COMP1531", algorithm = "HS256")

    filename = 'default.jpg'

    store['email'].append(email)
    store['password'].append(sha256(password.encode('utf-8')).hexdigest())
    store['name_first'].append(name_first)
    store['name_last'].append(name_last)
    store['user_id'].append(store['user_id_tracker'] + 1)
    store['user_id_tracker'] += 1
    store['token'].append([encoded_jwt])
    store['session_id'] += 1
    store['handle'].append(create_handle(name_first, name_last))
    store['profile_img_url'].append(f'{URL}/imgurl/{filename}')
    store["notifications"].append([])

    if store['user_id_tracker'] == 1:
        store['global_owners'].append(store['user_id_tracker'])

    data_store.set(store)

    return {
        "token": encoded_jwt, "auth_user_id": store['user_id_tracker']
    }

def auth_logout_v1(token):
    """
    Given an active token, invalidates the token to log the user out.
    Parameters: { token }
        - token (string): active token of user.
    Exceptions:
        - N/A
    Returns: If user is logged out, returns {}
        - {} (dictionary): empty dict.
    """
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

        for i in range(0, len(store['token'][index])):
            if store['token'][index][i] == token:
                store['token'][index][i] = sha256("invalidated_token".encode('utf-8')).hexdigest()

    data_store.set(store)

    return {}

def auth_passwordreset_request_v1(email):
    store = data_store.get()

    if email not in store['email']:
        return {}

    index = store['email'].index(email)

    for i in range(0, len(store['token'][index])):
        store['token'][index][i] = sha256("invalidated_token".encode('utf-8')).hexdigest()

    reset_code = jwt.encode({"email": email, "reset_code_id": store['reset_code_tracker'] + 1},
    "COMP1531", algorithm = "HS256")

    store['reset_code'].append(reset_code)
    store['reset_code_tracker'] += 1

    data_store.set(store)

    msg = EmailMessage()
    msg.set_content(f"G'day {store['name_first'][index]},\n\n" +
    f"Your Microsoft Seams password reset code:\n\n{reset_code}\n\n" +
    "Regards,\nMicrosoft Seams")

    msg['Subject'] = 'Microsoft Seams Password Reset Code'
    msg['From'] = "seams1531@gmail.com"
    msg['To'] = email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("seams1531@gmail.com", "COMP1531")
    server.send_message(msg)
    server.quit()

    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()

    if reset_code not in store['reset_code']:
        raise InputError("InputError: Reset code not valid")
    elif len(new_password) < 6:
        raise InputError("InputError: Password length too short")

    email = jwt.decode(reset_code, "COMP1531", algorithms = ['HS256'])['email']

    index = store['email'].index(email)
    store['password'][index] = (sha256(new_password.encode('utf-8')).hexdigest())

    index = store['reset_code'].index(reset_code)

    del store['reset_code'][index]

    data_store.set(store)

    return {}

