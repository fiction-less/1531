import sys
import signal
import pickle
import os
from json import dumps
from flask import Flask, request, Response, send_file
from flask_cors import CORS
from src.error import InputError
from src.data_store import data_store
from src import config
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.channel import channel_join_v1, channel_messages_v2, channel_invite_v1, channel_details_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.message import message_edit_v1, message_remove_v1, message_send_v1, message_send_dm_v1, message_pin_v1, message_unpin_v1, message_dm_send_later_v1, message_send_later_v1,  message_share_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.other import clear_v1
from src.user import user_profile_v1, user_profile_setname_v1, user_profile_setmail_v1, user_profile_sethandle_v1, user_profile_uploadphoto_v1
from src.users import users_all_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.search import search_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1
from src.notifications import notifications_get_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

with open('database.pickle', 'rb') as FILE:
    data = data_store.get()

    data = pickle.load(FILE)
    data_store.set(data)

def save():
    data = data_store.get()

    with open('database.pickle', 'wb') as FILE:
        pickle.dump(data, FILE)

@APP.route("/auth/register/v2", methods = ['POST'])
def auth_register_v2():
    """
    HTTP 'POST'
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
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    name_first = request_data['name_first']
    name_last = request_data['name_last']

    data = auth_register_v1(email, password, name_first, name_last)
    save()

    return dumps(data)

@APP.route("/auth/login/v2", methods = ['POST'])
def auth_login_v2():
    """
    HTTP 'POST'.
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
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']

    data = auth_login_v1(email, password)
    save()

    return dumps(data)

@APP.route("/auth/logout/v1", methods = ['POST'])
def auth_logout():
    """
    HTTP 'POST'.
    Given an active token, invalidates the token to log the user out.
    Parameters: { token }
        - token (string): active token of user.
    Exceptions:
        - N/A
    Returns: If user is logged out, returns {}
        - {} (dictionary): empty dict.
    """
    request_data = request.get_json()
    token = request_data['token']

    data = auth_logout_v1(token)
    save()

    return dumps(data)

@APP.route("/channels/create/v2", methods = ['POST'])
def channels_create_v2():
    """
    HTTP 'POST'.
    Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins the channel.
    Parameters: { token, name, is_public }
        - token (string): Token of channel creator/owner.
        - name (string): name of new channel.
        - is_public (bool): Privacy status of channel. True if public, false if private.
    Exceptions:
        - InputError: Occurs when;
            - length of name is less than 1 or more than 20 characters
    Returns: If channel is created, returns { channel_id }
        - channel_id (int): ID of created channel.
    """
    request_data = request.get_json()
    token = request_data['token']
    name = request_data['name']
    is_public = request_data['is_public']

    data = channels_create_v1(token, name, bool(is_public))
    save()
    return dumps(data)

@APP.route("/clear/v1", methods = ['DELETE'])
def clear():
    """
    HTTP 'DELETE'.
    Resets the internal data of the application to its initial state.
    Parameters:  {}
        - {} (dictionary): Empty dict.
    Exceptions:
        - N/A
    Returns: {}
        - {} (dictionary): Empty dict.
    """
    data = clear_v1()
    save()
    return dumps(data)

@APP.route("/channels/list/v2", methods = ['GET'])
def channels_list_v2():
    """
    HTTP 'GET'.
    Provide a list of all channels (and their associated details) that the authorised user is part of.
    Parameters: { token }
        - token (string): Authorised users token.
    Exceptions:
        - N/A
    Returns: { channels }
        - channels (List of dictionaries, where each dictionary contains types { channel_id, name }): list of channels authorised user is a part of.
    """
    token = request.args.get('token')

    data = channels_list_v1(token)
    save()

    return dumps(data)

@APP.route("/channels/listall/v2", methods = ['GET'])
def channels_listall_v2():
    """
    HTTP 'GET'.
    Provide a list of all channels, including private channels, (and their associated details).
    Parameters: { token }
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: { channels }
        - channels (List of dictionaries, where each dictionary contains types { channel_id, name }): list of channels authorised user is a part of.
    """
    token = request.args.get('token')

    data = channels_listall_v1(token)
    save()

    return dumps(data)

@APP.route("/channel/join/v2", methods = ['POST'])
def channel_join_v2():
    """
    HTTP 'POST'.
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.
    Parameters: { token, channel_id }
        - token (string): authorised users token
        - channel_id (int): ID of channel.
    Exceptions:
        InputError: Occurs when;
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel
        AccessError: Occurs when;
            - channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner
    Returns: {}
        - {} (dictionary): empty dict.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']

    data = channel_join_v1(token, int(channel_id))
    save()

    return dumps(data)

@APP.route("/channel/leave/v1", methods = ["POST"])
def channel_leave():
    """
    HTTP 'POST'
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel.
    Their messages should remain in the channel. If the only channel owner leaves, the channel will remain.
    Parameters: { token, channel_id }
        - token (string): authorised users token
        - channel_id (int): ID of channel being left.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
        - AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: {} (empty dictionary)
    """
    request_data = request.get_json()
    token = request_data["token"]
    channel_id = request_data["channel_id"]

    data = channel_leave_v1(token, int(channel_id))
    save()
    return dumps(data)

@APP.route("/channel/addowner/v1", methods = ["POST"])
def channel_addowner():
    """
    HTTP 'POST'
    Make user with user id u_id an owner of the channel.
    Parameters: { token, channel_id, u_id }
        - token (string): authorised users token
        - channel_id (int): ID of channel user will be added to.
        - u_id (int): ID of user to be added to channel.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not a member of the channel
            - u_id refers to a user who is already an owner of the channel
        - AccessError when:
            - channel_id is valid and the authorised user does not have owner permissions in the channel
    Returns: {} (empty dictionary)

    """
    request_data = request.get_json()
    token = request_data["token"]
    channel_id = request_data["channel_id"]
    u_id = request_data["u_id"]

    data = channel_addowner_v1(token, int(channel_id), int(u_id))
    save()
    return dumps(data)

@APP.route("/channel/removeowner/v1", methods = ["POST"])
def channel_removeowner():
    """
    HTTP 'POST'
    Remove user with user id u_id as an owner of the channel.
    Parameters: { token, channel_id, u_id }
        - token (string): token of authorised user.
        - channel_id (int): ID of channel user will be removed from.
        - u_id (int): ID of user to be removed from channel.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not an owner of the channel
            - u_id refers to a user who is currently the only owner of the channel
        - AccessError when:
            - channel_id is valid and the authorised user does not have owner permissions in the channel
    Returns: {} (empty dictionary)
    """
    request_data = request.get_json()
    token = request_data["token"]
    channel_id = request_data["channel_id"]
    u_id = request_data["u_id"]

    data = channel_removeowner_v1(token, int(channel_id), int(u_id))
    save()
    return dumps(data)

@APP.route("/channel/invite/v2", methods = ['POST'])
def channel_invite():
    """
    HTTP 'POST'
    Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately.
    In both public and private channels, all members are able to invite users.
    Parameters: { token, channel_id, u_id }
        - token (string): Authorised users token
        - channel_id (int): ID of channel that user will be invited to.
        - u_id (int): Users ID.
    Exceptions:
        - InputError when
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is already a member of the channel
        - AccessError when
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: {} (empty dictionary)
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']

    data = channel_invite_v1(token, int(channel_id), int(u_id))
    save()

    return dumps(data)


@APP.route("/channel/messages/v2", methods = ['GET'])
def channel_messages():
    """
    HTTP 'GET'
    Given a channel with ID channel_id that the authorised user is a member of, return up
    to 50 messages between index "start" and "start + 50". Message with index 0 is the most
    recent message in the channel. This function returns a new index "end" which is the
    value of "start + 50", or, if this function has returned the least recent messages
    in the channel, returns -1 in "end" to indicate there are no more messages to load
    after this return.
    Parameters: { token, channel_id, start }
        - token (string): authorised users token
        - channel_id (int): ID of channel to retrieve messages from
        - start (int): start index to start retrieving messages from.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
            - start is greater than the total number of messages in the channel
        - AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: If messages are successfully fetched, returns { messages, start, end }
        - messages (List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_sent })
        - start (int): start index
        - end (int): end index
    """

    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    data = channel_messages_v2(token, int(channel_id), int(start))
    save()

    return dumps(data)


@APP.route("/message/send/v1", methods = ['POST'])
def send_message():
    """
    HTTP 'POST'.
    Send a message from the authorised user to the channel specified by channel_id. Note: Each message should have its
    own unique ID, i.e. no messages should share an ID with another message, even if that other message is in a different channel.
    Parameters: { token, channel_id, message }
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
    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']

    data = message_send_v1(token, int(channel_id), message)
    save()

    return dumps(data)

@APP.route("/message/senddm/v1", methods = ['POST'])
def send_dm():
    """
    HTTP 'POST'.
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
    request_data = request.get_json()

    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']

    data = message_send_dm_v1(token, int(dm_id), message)
    save()

    return dumps(data)

@APP.route("/message/edit/v1", methods = ['PUT'])
def edit_message():
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
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    message = request_data['message']

    message_edit_v1(token, int(message_id), message)
    save()

    return dumps({})


@APP.route("/message/remove/v1", methods = ['DELETE'])
def remove_message():
    """
    HTTP 'DELETE'
    Given a message_id for a message, this message is removed from the channel/DM
    Parameters: { token, message_id }
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
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

    message_remove_v1(token, int(message_id))
    save()

    return dumps({})


@APP.route("/user/profile/v1", methods = ['GET'])
def user_profile():
    """
    HTTP 'GET'
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    Parameters: { token, u_id }
        - token (string): authorised users token.
        - u_id (int): ID of users profile.
    Exceptions:
        - InputError when
            - u_id does not refer to a valid user
    Returns: {user} if profile is successfully found.
        - user (dictionary): Dictionary containing u_id, email, name_first, name_last, handle_str
    """
    token = request.args.get('token')
    u_id = request.args.get('u_id')

    data = user_profile_v1(str(token), int(u_id))

    save()

    return dumps(data)

@APP.route("/user/profile/setname/v1", methods = ['PUT'])
def user_profile_setname():
    """
    HTTP 'PUT'
    Update the authorised user's first and last name
    Parameters: { token, name_first, name_last }
        - token (string): authorised users token
        - name_first (string): authorised users first name
        - name_last (string): authorised users last name.
    Exceptions:
        - InputError when:
            - length of name_first is not between 1 and 50 characters inclusive
            - length of name_last is not between 1 and 50 characters inclusive
    Returns: {} (empty dictionary) if authorised users name is successfuly updated.
    """
    request_data = request.get_json()
    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']

    data = user_profile_setname_v1(token, name_first, name_last)
    save()

    return dumps(data)

@APP.route("/user/profile/setemail/v1", methods = ['PUT'])
def user_profile_setmail():
    """
    HTTP 'PUT'
    Update the authorised user's email address
    Parameters: { token, email }
        - token: authorised users token
        - email: authorised users email.
    Exceptions:
        - InputError when:
            - email entered is not a valid email (more in section 6.4)
            - email address is already being used by another user
    Returns: {} (empty dictionary) if authorised users email address is successfuly updated.
    """
    request_data = request.get_json()
    token = request_data['token']
    email = request_data['email']

    data = user_profile_setmail_v1(token, email)
    save()

    return dumps(data)


@APP.route("/user/profile/sethandle/v1", methods = ['PUT'])
def user_profile_sethandle():
    """
    HTTP 'PUT'
    Update the authorised user's handle (i.e. display name)
    Parameters: { token, handle_str }
        - token (string): authorised users token
        - handle_str (string): authorised users new handle
    Exceptions:
        - InputError when any of:
            - length of handle_str is not between 3 and 20 characters inclusive
            - handle_str contains characters that are not alphanumeric
            - the handle is already used by another user
    Returns: {} (empty dictionary) if authorised users handle is successfully updated.
    """
    request_data = request.get_json()
    token = request_data['token']
    handle = request_data['handle_str']

    data = user_profile_sethandle_v1(token, handle)
    save()

    return dumps(data)

@APP.route("/users/all/v1", methods = ['GET'])
def users_all():
    """
    HTTP 'GET'
    Returns a list of all users and their associated details.
    Parameters:  {token}
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: {users} if list of users and details retrieved.
        - users (list of dictionaries): List of dictionaries, where each dictionary contains types of user
    """
    token = request.args.get('token')

    data = users_all_v1(token)
    save()

    return dumps(data)

@APP.route("/channel/details/v2", methods = ['GET'])
def channel_details_v2():
    """
    HTTP 'GET'
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
    Parameters: {token, channel_id}
        - token (string): authorised users token.
        - channel_id (int): ID of channel that authorised user is a part of.
    Exceptions:
        - InputError when
            - channel_id  does not refer to a valid channel.
        - AccessError when
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: { name, is_public, owner_members, all_members } if channel details are successfully retrieved
        - name (string): name of channel
        - is_public (bool): privacy setting of channel. True if public, false if private.
        - owner_members (list of dictionaries): list of owners of type 'user'
        - all_members (list of dictionaries): list of members of type 'user'.

    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    data = channel_details_v1(token, channel_id)
    save()

    return dumps(data)

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    """
    HTTP 'POST'
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. The creator is the owner of the DM.
    name should be automatically generated based on the users that are in this DM. The name should be an alphabetically-sorted,
    comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.
    Parameters: { token, u_ids }
        - token (string): authorised users token
        - u_ids (list): list of user_ids.
    Exceptions:
        - InputError when
            - any u_id in u_ids does not refer to a valid user
            - there are duplicate 'u_id's in u_ids
    Returns: {dm_id} if dm is successfully created.
        - dm_id (int): ID of created dm.
    """
    request_data = request.get_json()
    token = request_data['token']
    u_ids = request_data['u_ids']
    data = dm_create_v1(token, u_ids)
    save()
    return dumps(data)


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    """
    HTTP 'GET'
    Returns the list of DMs that the user is a member of.
    Parameters: {token}
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: {dms} if dm list is successfully retrieved.
        - dms (list): List of DMS that the user is a member of.
    """
    token = request.args.get('token')

    data = dm_list_v1(token)
    save()

    return dumps(data)


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    """
    HTTP 'DELETE'
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.
    Parameters: { token, dm_id }
        - token (string): original creators token
        - dm_id (int): ID of dm to be removed.
    Exceptions:
        - InputError when
            - dm_id does not refer to a valid
        - AccessError when
            - dm_id is valid and the authorised user is not the original DM creator
            - dm_id is valid and the authorised user is no longer in the DM
    Returns: {} (empty dictionary) if dm is successfully deleted.
    """
    request_data = request.get_json()
    token = request_data['token']
    dm_id = int(request_data['dm_id'])
    dm_remove_v1(token, dm_id)
    save()
    return dumps({})



@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    """
    HTTP 'GET'
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.
    Parameters: { token, dm_id }
        - token (string): authorised users token
        - dm_id (int): ID of dm
    Exceptions:
        - InputError when
            - dm_id does not refer to a valid DM
        - AccessError when
            - dm_id is valid and the authorised user is not a member of the DM
    Returns: { name, members } if dm details are successfully retrieved
        - name (string): dm name
        - members (list of dictionaries): List of dictionaries, where each dictionary contains types of user
    """
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    data = dm_details_v1(token, dm_id)
    save()

    return dumps(data)


@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    """
    HTTP 'POST'
    Given a DM ID, the user is removed as a member of this DM.
    The creator is allowed to leave and the DM will still exist if this happens. This does not update the name of the DM.
    Parameters: { token, dm_id }
        - token (string): users token
        - dm_id (int): ID of dm
    Exceptions:
        - InputError when:
            - dm_id does not refer to a valid DM
        - AccessError when:
            - dm_id is valid and the authorised user is not a member of the DM
    Returns:  {} (empty dictionary) if user successfully leaves dm.
    """
    request_data = request.get_json()
    token = request_data['token']
    dm_id = int(request_data['dm_id'])

    data = dm_leave_v1(token, dm_id)
    save()
    return dumps(data)


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    """
    HTTP 'GET'
    Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50".
     Message with index 0 is the most recent message in the DM. This function returns a new index "end" which is the value of
    "start + 50", or, if this function has returned the least recent messages in the DM, returns -1 in "end" to indicate there are no
    more messages to load after this return.
    Parameters: { token, dm_id, start }
        - token (string): authorised users token
        - dm_id (int): dm ID
        - start (int): start index.
    Exceptions:
        - InputError when:
            - dm_id does not refer to a valid DM
            - start is greater than the total number of messages in the channel
        - AccessError when:
            - dm_id is valid and the authorised user is not a member of the DM
    Returns: { messages, start, end }
        - messages (List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_sent })
        - start (int): start index
        - end (int):  end index
    """
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    data = dm_messages_v1(token, dm_id, start)
    save()

    return dumps(data)

@APP.route("/admin/user/remove/v1", methods = ["DELETE"])
def admin_userremove():
    """
    HTTP 'DELETE'
    Given a user by their u_id, remove them from the Seams. This means they should be removed from all channels/DMs,
    and will not be included in the list of users returned by users/all. Seams owners can remove other Seams owners
    (including the original first owner). Once users are removed, the contents of the messages they sent will be
    replaced by 'Removed user'. Their profile must still be retrievable with user/profile, however name_first
    should be 'Removed' and name_last should be 'user'. The user's email and handle should be reusable.
    Parameters: { token, u_id }
        - token (string): token of global woner
        - u_id (int): ID of user to be removed from seams.
    Exceptions:
        - InputError when
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner
        - AccessError when
            - the authorised user is not a global owner
    Returns: {} (empty dictionary) if user is successfully removed from seams.
    """
    request_data = request.get_json()
    token = request_data["token"]
    u_id = request_data["u_id"]

    data = admin_user_remove_v1(token, u_id)
    save()

    return dumps(data)

@APP.route("/admin/userpermission/change/v1", methods = ["POST"])
def admin_userpermission_change():
    """
    HTTP 'POST'
    Given a user by their user ID, set their permissions to new permissions described by permission_id.
    Parameters: { token, u_id, permission_id }
        - token (string): token of global owner
        - u_id (int): ID of user
        - permission_id (int): ID of new permission. 1 if owner, 2 if member.
    Exceptions:
        - InputError when
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner and they are being demoted to a user
            - permission_id is invalid
            - the user already has the permissions level of permission_id
    Returns: {} (empty dictionary) if user has their permissions successfully changed.
    """
    request_data = request.get_json()
    token = request_data["token"]
    u_id = request_data["u_id"]
    permission_id = request_data["permission_id"]

    data = admin_userpermission_change_v1(token, u_id, permission_id)
    save()

    return dumps(data)

@APP.route("/auth/passwordreset/request/v1", methods = ['POST'])
def auth_passwordreset_request():
    request_data = request.get_json()
    email = request_data["email"]

    data = auth_passwordreset_request_v1(email)
    save()

    return dumps(data)

@APP.route("/auth/passwordreset/reset/v1", methods = ['POST'])
def auth_passwordreset_reset():
    request_data = request.get_json()
    reset_code = request_data["reset_code"]
    new_password = request_data["new_password"]

    auth_passwordreset_reset_v1(reset_code, new_password)
    save()

    return dumps({})


@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin():

    request_data = request.get_json()

    token = request_data['token']
    message_id = request_data['message_id']

    message_pin_v1(token, int(message_id))
    save()

    return dumps({})

@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin():

    request_data = request.get_json()

    token = request_data['token']
    message_id = request_data['message_id']

    message_unpin_v1(token, int(message_id))
    save()

    return dumps({})

@APP.route("/imgurl/<filename>", methods = ['GET'])
def uploadphoto(filename):
    return send_file(f"{os.getcwd()}/imgurl/{filename}")



@APP.route("/user/profile/uploadphoto/v1", methods = ['POST'])
def user_profile_uploadphoto():
    request_data = request.get_json()

    token = request_data["token"]
    img_url = request_data["img_url"]
    x_start = request_data["x_start"]
    y_start = request_data["y_start"]
    x_end = request_data["x_end"]
    y_end = request_data["y_end"]

    data = user_profile_uploadphoto_v1(token, str(img_url), int(x_start), int(y_start),
    int(x_end), int(y_end))

    return dumps(data)

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    length = request_data['length']
    data = standup_start_v1(token, int(channel_id), int(length))
    save()
    return dumps(data)

@APP.route("/search/v1", methods = ["GET"])
def search():
    """
    Given a query string, return a collection of messages in all
    of the channels/DMs that the user has joined that contain the
    query (case-insensitive). There is no expected order for these messages.
    Args:
        - token (string): JWT of user.
        - query_str (string): Query string.
    Exceptions:
        - AccessError when:
            - Invalid token
        - InputError when:
            - query_str length < 1.
            - query_str length > 1000
    Returns:
        - {messages}: List of dictionaries, where each dictionary contains types
        { message_id, u_id, message, time_sent, reacts, is_pinned  }
    """
    token, query_str = request.args.get("token"), request.args.get("query_str")
    data = search_v1(token, query_str)
    return dumps(data)

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    data = standup_active_v1(token, channel_id)
    save()

    return dumps(data)


@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    data = standup_send_v1(token, int(channel_id), message)
    save()
    return dumps(data)

@APP.route("/message/sendlater/v1", methods = ['POST'])
def message_send_later():

    request_data = request.get_json()

    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    data = message_send_later_v1(token, channel_id, message, time_sent)
    save()
    return dumps(data)

@APP.route("/message/sendlaterdm/v1", methods = ['POST'])
def message_senddm_later():

    request_data = request.get_json()

    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    data = message_dm_send_later_v1(token, dm_id, message, time_sent)
    save()
    return dumps(data)


@APP.route("/message/share/v1", methods = ["POST"])
def message_share():
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
    request_data = request.get_json()

    # Unpacking variables.
    token = request_data["token"]
    og_message_id = request_data["og_message_id"]
    message = request_data["message"]
    channel_id = request_data["channel_id"]
    dm_id = request_data["dm_id"]

    data = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    save()

    return dumps(data)

@APP.route("/notifications/get/v1", methods = ["GET"])
def notifications_get():
    """
    Return a user's most recent 20 notifications, ordered from most recent to least recent.
    Args:
        - token (string): user's token.
    Exceptions:
        - AccessError when:
            - token invalid.
    Returns:
        - {notifications} (list of dictionaries): dictionary is of type {channel_id, dm_id, notification_message}
            - channel_id (int): ID of channel notification event occured. -1 if it occured in a DM.
            - dm_id (int): ID of dm notification event occured. -1 if it occured in a channel.
            - notification_message (string): string of the follow formats for each action.
                -tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
                - reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
                - added to a channel/DM: "{User’s handle} added you to {channel/DM name}"
    """
    token = request.args.get("token")
    data = notifications_get_v1(token)
    save()
    return dumps(data)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
