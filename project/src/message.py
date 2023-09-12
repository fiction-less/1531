''' Implementation for message.py
Written 25/03/22
by Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

import time
import threading
import re

from threading import Timer

from email import message
from webbrowser import get
from src.data_store import data_store
from src.error import AccessError, InputError
from src.channels import channels_list_v1, channels_create_v1
from src.dm import dm_list_v1
from src.other import get_index

def check_token(token):
    store = data_store.get()
    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")


def get_user_uid(token):
    store = data_store.get()
    for idx, tokens in enumerate(store['token']):
        for i in tokens:
            if i == token:
                uid = store['user_id'][idx]
    return uid

# the index is the index of the channel the message_id is in
def check_message_in_user_joined_channels(index, token):
    '''checks if the message is in the channel the use has joined'''
    store = data_store.get()
    msg_in_channel = False
    channels = channels_list_v1(token)
    msg_channel = store['channel_id'][index]
    for channel in channels['channels']:
        if channel['channel_id'] == msg_channel:
            msg_in_channel = True
            break
    if msg_in_channel == False:
        raise InputError(description = "InputError: message_id not in channel")

# the index is the index of the DM the message_id is in
def check_message_in_user_joined_DMs(index, token):
    store = data_store.get()
    msg_in_DM = False
    dms = dm_list_v1(token)
    msg_DM = store['dm_id'][index]
    for dm in dms['dms']:
        if dm['dm_id'] == msg_DM:
            msg_in_DM = True
            break
    if msg_in_DM == False:
        raise InputError(description = "InputError: message_id not in DM")


def search_for_message(message_id):
    '''search all channel and DM messages using the message_ID, if found, returns a dict {datastore,
       uid, message_idx and index}, else returns false'''

    store = data_store.get()

    counter = 0
    for channel in store['channel_messages']:
        for i, messages in enumerate(channel):
            if messages['message_id'] == message_id:
                dict = {
                    'store': store['channel_messages'],
                    'auth_uid': messages['u_id'],
                    'msg_idx':  i,
                    'index':counter
                }
                return dict
        counter += 1

    #search DM
    counter = 0
    for dm in store['dm_messages']:
        for i, message in enumerate(dm):
            if message['message_id'] == message_id:
                dict = {
                    'store': store['dm_messages'],
                    'auth_uid': message['u_id'],
                    'msg_idx':  i,
                    'index':counter # the DM they found the message in
                }
                return dict
        counter += 1

    return False


def check_permission_channels (index, token, token_uid):
    '''if no owners permission and not a global owner channel, raise error'''

    store = data_store.get()
    check_message_in_user_joined_channels(index, token)
    if  token_uid not in store['channel_owner_members'][index] and \
        token_uid not in store['global_owners']:
        raise AccessError(description = "AccessError: You do not have permission to perform this action")

def check_permission_DM (index, token, token_uid):
    '''if no owners permission and not a global owner channel, raise error'''
    store = data_store.get()
    check_message_in_user_joined_DMs(index, token)
    if  token_uid != store['dm_owner'][index]:
        raise AccessError(description = "AccessError: You do not have permission to perform this action")

def check_for_tags(msg, ch_id, dm_id):
    """
    Helper function to check for tags in a message. E.g. "@handle hello!" or "@handle hi!".
    If there are valid tags, it will append them to the tagged user/s notifications.
    Args:
        - msg (string): message to be checked.
        - ch_id (int): ID of channel the tag happened in. -1 if it happened in a dm.
        - dm_id (int): ID of dm the tag happened in. -1 if it happened in a channel.
    Exceptions: None
    Return: None
    """
    store = data_store.get()

    # Message came from a channel.
    if dm_id == -1:
        ch_idx = store["channel_id"].index(ch_id)
        ch_name = store["channel_name"][ch_idx]
        # Loop through each users handle, looking for tags.
        for user_handle in store["handle"]:
            u_idx = store["handle"].index(user_handle)
            u_id = store["user_id"][u_idx]
            u_handle = store["handle"][u_idx]
            if f"@{user_handle}" in msg and u_id in store["channel_all_members"][ch_idx]:
                print(user_handle)
                store["notifications"][u_idx].append({
                    "channel_id": ch_id,
                    "dm_id": dm_id,
                    "notification_message": f"{u_handle} tagged you in {ch_name}: {msg[0:20]}"
                })

    # Message came from a dm.
    if ch_id == -1:
        dm_idx = store["dm_id"].index(dm_id)
        dm_name = store["dm_name"][dm_idx]
        # Loop through each users handle, looking for tags.
        for user_handle in store["handle"]:
            u_idx = store["handle"].index(user_handle)
            u_id = store["user_id"][u_idx]
            u_handle = store["handle"][u_idx]
            if f"@{user_handle}" in msg and (u_id == store["dm_owner"][dm_idx] or u_id in store["dm"][dm_idx]):
                store["notifications"][u_idx].append({
                    "channel_id": ch_id,
                    "dm_id": dm_id,
                    "notification_message": f"{u_handle} tagged you in {dm_name}: {msg[0:20]}"
                })


def message_send_v1(token, channel_id, message, message_id=None):
    """
    Send a message from the authorised user to the channel specified by channel_id. Note: Each message should have its
    own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel.
    Parameters:
        - token (string): authorised users token
        - channel_id (int): ID of specified channel
        - message (string): message to be sent.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
            - length of message is less than 1 or over 1000 characters
        - AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: If message is succesfully sent, returns { message_id }
        - message_id (int): ID of message sent.
    """

    store = data_store.get()

    # if message id is None, it means that its not a message being sent later
    # if the message_id is given a value, then that is the message id given to the future message.
    # this ensures message_tracker does not make a new message id for the future message when the time comes

    if message_id == None:
        store['message_id_tracker'] += 1
        message_id = store['message_id_tracker']

    print("message id", message_id)

    if channel_id not in store['channel_id']:
        raise InputError(description = "InputError: channel_id does not refer to a valid channel")

    check_token(token)

    uid = get_user_uid(token)
    index = store['channel_id'].index(channel_id)

    if uid not in store['channel_all_members'][index]:
        raise AccessError(description = "AccessError: Authorised user is not a member of the channel")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(description = "InputError: Messages must be between length 1 - 100, inclusive")

    timestamp = int(time.time())

    store['channel_messages'][index].append({
        'message_id':store['message_id_tracker'],
        'u_id': uid,
        'message': message,
        'time_sent': timestamp,
        'reacts': [],
        'is_pinned': False
    })

    check_for_tags(message, channel_id, -1)  # Checking for tags in the message.

    data_store.set(store)

    return {
        'message_id': message_id
    }



def message_edit_v1(token, message_id, message):
    """
    HTTP 'PUT'
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    Parameters:  { token, message_id, message }
        - token (string): authorised users token.
        - message_id (int): ID of message to be edited
        - message (string): new message.
    Exceptions:
        - InputError when
            - length of message is over 1000 characters
            - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        - AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
            - the message was sent by the authorised user making this request
            - the authorised user has owner permissions in the channel/DM
    Returns: {} (empty dictionary) if message is succesfully edited.
    """

    store = data_store.get()

    check_token(token)

    dict = search_for_message(message_id)
    if dict == False:
        raise InputError(description = "InputError: message_id does not exist")

    store_msg = dict['store']
    sender_uid = dict['auth_uid']
    msg_idx = dict['msg_idx']
    index = dict['index']

    token_uid = get_user_uid(token)

    # channel: if not sender of message AND not doesnt have owners permission= NOT and not a global owner channel:

    if store_msg == store['channel_messages']:
        if token_uid != sender_uid:
            check_permission_channels (index, token, token_uid)


    if store_msg == store['dm_messages']:
        if token_uid != sender_uid:
            check_permission_DM (index, token, token_uid)

    if len(message) > 1000:
        raise InputError(description = "InputError: Length of message must be between 1 and 1000")

    if message == "":
        del store_msg[index][msg_idx]
    else:
        store_msg[index][msg_idx]['message'] = message

    data_store.set(store)

    return {}



def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM
    Parameters:
        - token (string): authorised users token
        - message_id (int): ID of message to be removed.
    Exceptions:
        - InputError when
            - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        - AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
            - the message was sent by the authorised user making this request
            - the authorised user has owner permissions in the channel/DM
    Returns: {} (empty dictionary) if the message was successfully removed.
    """
    store = data_store.get()

    check_token(token)

    dict = search_for_message(message_id)
    if dict == False:
        raise InputError(description = "InputError: message_id does not exist")

    store_msg = dict['store']
    sender_uid = dict['auth_uid']
    msg_idx = dict['msg_idx']
    index = dict['index'] # this index is of the channel they found the message in

    token_uid = get_user_uid(token)

    # channel: if not sender of message AND not doesnt have owners permission= NOT and not a global owner channel:
    if store_msg == store['channel_messages']:
        if token_uid != sender_uid:
            check_permission_channels (index, token, token_uid)

    ## DM:
    if store_msg == store['dm_messages']:
        if token_uid != sender_uid:
            check_permission_DM (index, token, token_uid)

    del store_msg[index][msg_idx]

    data_store.set(store)

    return {}

def message_send_dm_v1(token, dm_id, message, message_id = None):
    """
    Send a message from the authorised user to the dm specified by dm_id. Note: Each message should have its
    own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel or DM.
    Parameters: { token, channel_id, message }
        - token (string): authorised users token
        - dm_id (int): ID of specified dm
        - message (string): message to be sent.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid dm
            - length of message is less than 1 or over 1000 characters
        - AccessError when:
            - dm_id is valid and the authorised user is not a member of the dm
    Returns: If message is succesfully sent, returns { message_id }
        - message_id (int): ID of message sent.
    """
    store = data_store.get()

    if message_id == None:
        store['message_id_tracker'] += 1
        message_id = store['message_id_tracker']


    if dm_id not in store['dm_id']:
        raise InputError(description = "InputError: dm_id does not refer to a valid channel")

    check_token(token)

    uid = get_user_uid(token)
    # since DMs can be deleted, grab index instead of dm_id - 1
    index = store['dm_id'].index(dm_id)

    # if person sending is not an owner or a member
    if uid not in store['dm'][index] and uid != store['dm_owner'][index]:
        raise AccessError(description = "AccessError: Authorised user is not a member of the DM")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(description = "InputError: Messages must be between length 1 - 100, inclusive")

    timestamp = int(time.time())


    store['dm_messages'][index].append({
        'message_id':store['message_id_tracker'],
        'u_id': uid,
        'message': message,
        'time_sent': timestamp,
        'reacts': [],
        'is_pinned': False
    })

    check_for_tags(message, -1, dm_id)  # Checking for tags in the message.

    data_store.set(store)

    return {

        'message_id': message_id
    }



def do_pinned (store_msg, msg_idx, index):
    '''index refers to the channel/DM index, checks if message if already pinned, if not, pins it'''

    if store_msg[index][msg_idx]['is_pinned'] == True:
        raise InputError(description = "InputError: message already pinned")

    store_msg[index][msg_idx]['is_pinned'] = True


def do_unpinned (store_msg, msg_idx, index):
    '''index refers to the channel/DM index, checks if message if unpinned, if not, unpins it'''

    if store_msg[index][msg_idx]['is_pinned'] == False:
        raise InputError(description = "InputError: message is not pinned")

    store_msg[index][msg_idx]['is_pinned'] = False

def message_pin_v1(token, message_id):
    '''Given a message within a channel or DM, mark it as pinned'''

    store = data_store.get()
    check_token(token)

    dict = search_for_message(message_id)
    if dict == False:
        raise InputError(description = "InputError: message_id does not exist")

    store_msg = dict['store']
    msg_idx = dict['msg_idx']
    index = dict['index'] # this index is of the channel/DM they found the message in

    token_uid = get_user_uid(token)

    # message_id is not a valid message within a channel or DM that the authorised user has joined

    if store_msg == store['channel_messages']:
        check_permission_channels (index, token, token_uid)
        do_pinned(store_msg, msg_idx, index)


    elif store_msg == store['dm_messages']:
        check_permission_DM (index, token, token_uid)
        do_pinned(store_msg, msg_idx, index)

    return {}

def message_unpin_v1(token, message_id):
    '''Given a message within a channel or DM, mark it as pinned'''

    store = data_store.get()
    check_token(token)

    dict = search_for_message(message_id)
    if dict == False:
        raise InputError(description = "InputError: message_id does not exist")

    store_msg = dict['store']
    msg_idx = dict['msg_idx']
    index = dict['index'] # this index is of the channel/DM they found the message in

    token_uid = get_user_uid(token)

    # message_id is not a valid message within a channel or DM that the authorised user has joined

    if store_msg == store['channel_messages']:
        check_permission_channels (index, token, token_uid)
        do_unpinned(store_msg, msg_idx,index)

    elif store_msg == store['dm_messages']:
        check_permission_DM (index, token, token_uid)
        do_unpinned(store_msg, msg_idx, index)

    return {}


def message_send_later_v1(token, channel_id, message, time_sent):
    store = data_store.get()

    if channel_id not in store['channel_id']:
        raise InputError(description = "InputError: channel_id does not refer to a valid channel")

    check_token(token)

    uid = get_user_uid(token)
    index = store['channel_id'].index(channel_id)

    if uid not in store['channel_all_members'][index]:
        raise AccessError(description = "AccessError: Authorised user is not a member of the channel")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(description = "InputError: Messages must be between length 1 - 100, inclusive")

    curr_time = int(time.time())
    countdown = time_sent - curr_time

    if countdown < 0:
        raise InputError(description = "InputError: invalid time")

    # need to return the message id straight away, even if message isnt sent, that message id cannot be used to edit or delete
    # message_tracker only tracks the id, even if its tracked, you cant actually access it to use it
    # the only way to find and use a message is is through channel/dM messages or search_for_message
    store['message_id_tracker'] += 1
    message_id = store['message_id_tracker']

    send_message = threading.Timer(countdown, message_send_v1, [token, channel_id, message, message_id])
    send_message.start()


    return {
        'message_id': message_id
    }


def message_dm_send_later_v1(token, dm_id, message, time_sent):
    store = data_store.get()

    if dm_id not in store['dm_id']:
        raise InputError(description = "InputError: dm_id does not refer to a valid channel")

    check_token(token)

    uid = get_user_uid(token)
    # since DMs can be deleted, grab index instead of dm_id - 1
    index = store['dm_id'].index(dm_id)

    # if person sending is not an owner or a member
    if uid not in store['dm'][index] and uid != store['dm_owner'][index]:
        raise AccessError(description = "AccessError: Authorised user is not a member of the DM")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(description = "InputError: Messages must be between length 1 - 100, inclusive")


    curr_time = int(time.time())
    countdown = time_sent - curr_time

    if countdown < 0:
        raise InputError(description = "InputError: invalid time")

    # need to return the message id straight away, even if message isnt sent, that message id cannot be used to edit or delete
    # message_tracker only tracks the id, even if its tracked, you cant actually access it to use it
    # the only way to find and use a message is is through channel/dM messages or search_for_message
    store['message_id_tracker'] += 1
    message_id = store['message_id_tracker']

    send_message = threading.Timer(countdown, message_send_dm_v1, [token, dm_id, message, message_id])
    send_message.start()

    return {
        'message_id': message_id
    }



def find_message(msg_id, u_id):
    """
    Helper function to find if a message exists in channels a user (specified by ID)
    is a part of.
    Args:
        - msg_id (int): ID of message.
        - u_id (int): ID of user.
    Exceptions: N/A.
    Returns: Tuple containing:
        - msg_found (bool): True if message was found. False if message was not found.
        - msg (dict): Message 'msg_id' refers to. {} (empty dict) if message was not found.
    """
    store = data_store.get()

    msg_found = 0
    msg = {}

    # Finding message in dms.
    for dm in store["dm_messages"]:
        dm_idx = store["dm_messages"].index(dm)
        for message in dm:
            if (u_id == store["dm_owner"][dm_idx] or u_id in store["dm"][dm_idx]) and message["message_id"] == msg_id:
                msg_found = 1
                msg = message

    # Finding message in channels.
    for channel in store["channel_messages"]:
        ch_idx = store["channel_messages"].index(channel)
        for message in channel:
            if u_id in store["channel_all_members"][ch_idx] and message["message_id"] == msg_id:
                msg_found = 1
                msg = message
    return (msg_found, msg)


def message_share_v1_error_checks(token, og_message_id, message, channel_id, dm_id):
    """
    Error checker helper function for message/share/v1.
    Args:
        - token (string): Web token of user who is sharing the message.
        - og_message_id (int): ID of original meesage.
        - message (string): Optional message attached to original message. "" if no message given.
        - channel_id (int): ID of channel the message is being shared to. -1 if message is being shared to a dm.
        - dm_id (int): ID of dm the message being shared to. -1 if message is being shared to a channel.
    Exceptions:
        - InputError when:
            - channel_id and dm_id are both invalid.
            - neither channel_id or dm_id are -1.
            - og_message_id does not refer to a message within a channel/dm the user has joined.
            - length of message is greater than 1000 characters.
        - AccessError when:
            - dm_id and channel_id are both valid (one is -1, other is valid) & authorised user has not joined
            the dm/channel they are trying to share the message to.
            - token is invalid.
    Returns:
        - shared_message_id (int): ID of new message belonging to a channel/dm.
    """
    store = data_store.get()

    # Raise AccessError if token is invalid.
    if not any(token in user_tokens for user_tokens in store["token"]):
        raise AccessError(description = "message/share/v1 -> Invalid Token")

    # Finding token owners user ID.
    u_id = store["user_id"][get_index(token)]

    # Raise InputError if channel_id and dm_id are both invalid.
    if channel_id not in store["channel_id"] and dm_id not in store["dm_id"]:
        raise InputError("message/share/v1 -> channel_id and dm_id are both invalid.")

    # Raise InputError if neither channel_id or dm_id are -1.
    if channel_id != -1 and dm_id != -1:
        raise InputError("message/share/v1 -> neither channel_id or dm_id are -1.")

    # Raise InputError if og_message_id does not refer to a valid message within a channel/dm the user has joiend.
    if not find_message(og_message_id, u_id)[0]:
        raise InputError("message/share/v1 -> og_message_id does not refer to a valid message within a channel/dm the user has joined.")

    # Raise InputError if length of message is more than 1000 characters.
    if len(message) > 1000:
        raise InputError("message/share/v1 -> length of message is more than 1000 characters.")

    # Raise AccessError if authorised user has not joined the dm they are trying to share to.
    if channel_id == -1 and dm_id in store["dm_id"]:
        dm_idx = store["dm_id"].index(dm_id)
        if u_id not in store["dm"][dm_idx] and u_id != store["dm_owner"][dm_idx]:
            raise AccessError("message/share/v1 -> authorised user has not joined the dm they are trying to send to.")

    # Raise AccessError if authorised user has not joined the channel they are trying to share to.
    if dm_id == -1 and channel_id in store["channel_id"]:
        ch_idx = store["channel_id"].index(channel_id)
        if u_id not in store["channel_all_members"][ch_idx]:
            raise AccessError("message/share/v1 -> authorised user has not joined the channel they are trying to send to.")


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    Given a valid token, share a message (specified by ID) to a channel or dm (specified by ID).
    An optional message can also be added to the shared message (default empty string "").
    Args:
        - token (string): Web token of user who is sharing the message.
        - og_message_id (int): ID of original meesage.
        - message (string): Optional message attached to original message. "" if no message given.
        - channel_id (int): ID of channel the message is being shared to. -1 if message is being shared to a dm.
        - dm_id (int): ID of dm the message being shared to. -1 if message is being shared to a channel.
    Exceptions:
        - InputError when:
            - channel_id and dm_id are both invalid.
            - neither channel_id or dm_id are -1.
            - og_message_id does not refer to a message within a channel/dm the user has joined.
            - length of message is greater than 1000 characters.
        - AccessError when:
            - dm_id and channel_id are both valid (one is -1, other is valid) & authorised user has not joined
            the dm/channel they are trying to share the message to.
            - token is invalid.
    Returns:
        - shared_message_id (int): ID of new message belonging to a channel/dm.
    """
    store = data_store.get()

    # Error checks
    message_share_v1_error_checks(token, og_message_id, message, channel_id, dm_id)

    # Finding token owners user ID.
    u_id = store["user_id"][get_index(token)]

    # Finding message 'og_message_id refers to and creating new message.
    og_msg = find_message(og_message_id, u_id)[1]
    new_msg = og_msg["message"] + message

    # Updating message tracker and finding ID of new message.
    store["message_id_tracker"] += 1
    new_msg_id = store["message_id_tracker"]

    # Message is being sent to a channel - append new message to channel.
    if dm_id == -1:
        ch_idx = store["channel_id"].index(channel_id)
        store["channel_messages"][ch_idx].append({
            "message_id": store["message_id_tracker"],
            "u_id": u_id,
            "message": new_msg,
            "time_sent": int(time.time()),
            "reacts": [],
            "is_pinned": False
        })

    # Message is being sent to a dm - append new message to dm.
    if channel_id == -1:
        dm_idx =  store["dm_id"].index(dm_id)
        store["dm_messages"][dm_idx].append({
            "message_id": new_msg_id,
            "u_id": u_id,
            "message": new_msg,
            "time_sent": int(time.time()),
            "reacts": [],
            "is_pinned": False
        })

    check_for_tags(new_msg, channel_id, dm_id)  # Checking for tags in the new message.

    return {"shared_message_id": new_msg_id}
