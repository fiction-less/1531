''' Implementation of user functions
Written 21/03/22
by Alyssa Lubrano (z5362292@ad.unsw.edu.au) and Aryan Bahinipati (z5310696@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.data_store import data_store
from src.error import AccessError, InputError
from src.auth import valid_email
from src.other import get_index
from src import config
from urllib import request as ulreq
from PIL import ImageFile
from PIL import Image
from uuid import uuid4

import subprocess
import sys
import urllib.request
import urllib
import requests
import shutil
import os

URL = f'http://localhost:{config.port}'

def user_profile_v1(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    Parameters:
        - token (string): authorised users token.
        - u_id (int): ID of users profile.
    Exceptions:
        - InputError when
            - u_id does not refer to a valid user
    Returns: {user} if profile is successfully found.
        - user (dictionary): Dictionary containing u_id, email, name_first, name_last, handle_str
    """
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    if u_id not in store['user_id']:
        raise InputError(description = "InputError: User id invalid")

    index = store['user_id'].index(u_id)

    user = {'user': {"u_id": store['user_id'][index], "email": store['email'][index],
    "name_first": store['name_first'][index], "name_last": store['name_last'][index],
    "handle_str": store['handle'][index], "profile_img_url": store['profile_img_url'][index]}}

    return user

def user_profile_setname_v1(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    Parameters:
        - token (string): authorised users token
        - name_first (string): authorised users first name
        - name_last (string): authorised users last name.
    Exceptions:
        - InputError when:
            - length of name_first is not between 1 and 50 characters inclusive
            - length of name_last is not between 1 and 50 characters inclusive
    Returns: {} (empty dictionary) if authorised users name is successfuly updated.
    """

    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description = "InputError: First name not valid length")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description = "InputError: Last name not valid length")

    index = get_index(token)

    store['name_first'][index] = name_first
    store['name_last'][index] = name_last

    data_store.set(store)

    return {}

def user_profile_setmail_v1(token, email):
    """
    Update the authorised user's email address
    Parameters:
        - token: authorised users token
        - email: authorised users email.
    Exceptions:
        - InputError when:
            - email entered is not a valid email (more in section 6.4)
            - email address is already being used by another user
    Returns: {} (empty dictionary) if authorised users email address is successfuly updated.
    """
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    if valid_email(email) == False:
        raise InputError(description = "InputError: Invalid email")
    if email in store['email']:
        raise InputError(description = "InputError: Email is already linked to an account")

    index = get_index(token)

    store['email'][index] = email

    data_store.set(store)

    return {}

def user_profile_sethandle_v1(token, handle):
    """
    Update the authorised user's handle (i.e. display name)
    Parameters:
        - token (string): authorised users token
        - handle_str (string): authorised users new handle
    Exceptions:
        - InputError when any of:
            - length of handle_str is not between 3 and 20 characters inclusive
            - handle_str contains characters that are not alphanumeric
            - the handle is already used by another user
    Returns: {} (empty dictionary) if authorised users handle is successfully updated.
    """
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    if len(handle) < 3 or len(handle) > 20:
        raise InputError(description = "InputError: Handle must be within 3 and 20 characters")
    if handle in store['handle']:
        raise InputError(description = "InputError: Handle is already linked to an account")

    index = get_index(token)

    store['handle'][index] = handle

    data_store.set(store)

    return {}

def check_url(url):
    """ Returns True if the url returns a response code is 200,
        otherwise return False """

    response = requests.get(url)

    if response.status_code == 200:
        return True
    else:
        return False

def image_size(url):
    file = ulreq.urlopen(url)
    size = file.headers.get("content-length")

    if size:
        size = int(size)

    p = ImageFile.Parser()

    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return p.image.size

    file.close()

    return (size, None)

def user_profile_uploadphoto_v1_checks(token, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    elif check_url(img_url) == False:
        raise InputError(description = "InputError: Could not retrieve image")

    size = image_size(img_url)

    if (x_start < 0 or x_start > size[0] or y_start < 0 or y_start > size[1] or
    x_end < 0 or x_end > size[0] or y_end < 0 or y_end > size[1]):
        raise InputError(description = "InputError: x and y positions are not within image")
    elif x_end <= x_start or y_end <= y_start:
        raise InputError(description = "InputError: End dimensions greater or equal to start dimensions")
    elif requests.head(img_url).headers["content-type"] not in ['image/jpg', 'image/jpeg']:
        raise InputError(description = "InputError: Url not jpg type")

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()

    user_profile_uploadphoto_v1_checks(token, img_url, x_start, y_start, x_end, y_end)

    rand_token = uuid4()
    filename = f'{rand_token}.jpg'

    urllib.request.urlretrieve(img_url, filename)
    img = Image.open(filename).convert('RGB')
    img_crop = img.crop((x_start, y_start, x_end, y_end))
    img_crop.save(filename)

    src_path = f"{os.getcwd()}/{filename}"
    dst_path = f"{os.getcwd()}/imgurl/{filename}"

    shutil.move(src_path, dst_path)

    index = get_index(token)

    store['profile_img_url'][index] = f'{URL}/imgurl/{filename}'

    data_store.set(store)

    return {}

