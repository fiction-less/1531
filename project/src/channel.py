''' Implementation of channel functions
Written 25/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au), Daniel Wang (z5312741@ad.unsw.edu.au) and Kelly Xu (z5285375@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.channels import channels_create_v1
from src.data_store import data_store
from src.error import AccessError, InputError
from src.message import get_user_uid
from src.other import get_index

def channel_invite_v1(token, channel_id, u_id):
    """
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

    store = data_store.get()

    if channel_id not in store['channel_id']:
        raise InputError(description = "Input error: Invalid channel")

    index = store['channel_id'].index(channel_id)

    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")

    if u_id not in store['user_id']:
        raise InputError(description = "Input error: Invalid User ID")

    token_uid = get_user_uid(token)
    if u_id in store['channel_all_members'][index]:
        raise InputError(description = "Input error: User already member of channel")
    if token_uid not in store['channel_all_members'][index]:
        raise AccessError(description = "Access error: Authorised user not in channel.")

    index = store['channel_id'].index(channel_id)
    store['channel_all_members'][index].append(u_id)

    # Sending notification to user.
    user_index = store["user_id"].index(u_id)
    user_handle = store["handle"][user_index]
    channel_name = store["channel_name"][index]
    store["notifications"][user_index].append({
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": f"{user_handle} added you to {channel_name}"
    })

    data_store.set(store)

    return {}


def channel_details_v1_checks(token, channel_id):
    ''' Checks for any InputError or AccessError when given details
        Input: auth_user_id, channel_id
        Output: raiseInputError, raiseAccessError '''

    store = data_store.get()

    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")

    if channel_id not in store['channel_id']:
        raise InputError(description = "InputError: channel_id does not refer to a valid channel")
    else:
        index = get_index(token)

        auth_user_id = store['user_id'][index]

        index = store['channel_id'].index(channel_id)

        if auth_user_id not in store['channel_all_members'][index]:
            raise AccessError(description = "AccessError: Authorised user is not a member of the channel")

def channel_details_v1(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
    Parameters:
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

    store = data_store.get()

    channel_details_v1_checks(token, channel_id)

    index = store['channel_id'].index(channel_id)

    publicity_status = store['channel_is_public'][index]
    details = {'name': store['channel_name'][index], 'is_public': publicity_status, 'owner_members': [], 'all_members': []}

    for i in store['channel_owner_members'][index]:
        user_index = store['user_id'].index(i)

        data = {'u_id': store['user_id'][user_index], 'email': store['email'][user_index],
                'name_first': store['name_first'][user_index], 'name_last': store['name_last'][user_index],
                'handle_str': store['handle'][user_index]}

        details['owner_members'].append(data)

    for i in store['channel_all_members'][index]:
        user_index = store['user_id'].index(i)

        data = {'u_id': store['user_id'][user_index], 'email': store['email'][user_index],
                'name_first': store['name_first'][user_index], 'name_last': store['name_last'][user_index],
                'handle_str': store['handle'][user_index]}

        details['all_members'].append(data)

    return details


def channel_messages_v2(token, channel_id, start):
    """
    Given a channel with ID channel_id that the authorised user is a member of, return up
    to 50 messages between index "start" and "start + 50". Message with index 0 is the most
    recent message in the channel. This function returns a new index "end" which is the
    value of "start + 50", or, if this function has returned the least recent messages
    in the channel, returns -1 in "end" to indicate there are no more messages to load
    after this return.
    Parameters:
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

    store = data_store.get()

    if channel_id not in store['channel_id']:
        raise InputError(description = "InputError: channel_id does not refer to a valid channel")

    index = store['channel_id'].index(channel_id)
    num_messages = len(store['channel_messages'][index])

    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")

    uid = get_user_uid(token)

    if uid not in store['channel_all_members'][index]:
        raise AccessError(description = "AccessError: Authorised user is not a member of the channel")

    if start > num_messages:
        raise InputError(description = "InputError: Start greater than total number of messages in channel")
    if start < 0:
        raise InputError(description = "InputError: Invalid start")

    store['channel_messages'][index].reverse()

    end = start + 50
    return_messages = []

    # once all messages have been printed, make end -1 ( less than 50 messages to be printed)
    if num_messages <= end:
        i = start
        while i < num_messages:
            return_messages.append(store['channel_messages'][index][i])
            i += 1
        end = -1
    # returns 50 messages, newest to oldest
    else:
        i = start
        while i < end:
            return_messages.append(store['channel_messages'][index][i])
            i += 1

    store['channel_messages'][index].reverse()

    return {
        'messages': return_messages,
        'start': start,
        'end': end,
    }



def channel_join_v1_checks(token, channel_id):
    """
    Helper function for channel_join_v1 to check for errors.
    Parameters: { token, channel_id }
        - token (string): authorised users token
        - channel_id (int): ID of channel.
    Exceptions:
        InputError: Occurs when;
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel
        AccessError: Occurs when;
            - channel_id refers to a channel that is private and the authorised user
            is not already a channel member and is not a global owner
    Returns: {}
        - {} (dictionary): empty dict.
    """

    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")

    index = get_index(token)

    auth_user_id = store['user_id'][index]

    if channel_id not in store['channel_id']:
        raise InputError(description = "InputError: Invalid channel ID.")

    index = store['channel_id'].index(channel_id)

    if auth_user_id in store['channel_all_members'][index]:
        raise InputError(description = "InputError. Authorised user is already a member of the channel")

    if store['channel_is_public'][index] == False and auth_user_id not in store['global_owners']:
        raise AccessError(description = "AccessError: Private channel, user is not an member/owner.")

def channel_join_v1(token, channel_id):
    """
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.
    Parameters:
        - token (string): authorised users token
        - channel_id (int): ID of channel.
    Exceptions:
        InputError: Occurs when;
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel
        AccessError: Occurs when;
            - channel_id refers to a channel that is private and the
            authorised user is not already a channel member and is not a global owner
    Returns: {}
        - {} (dictionary): empty dict.
    """

    store = data_store.get()
    channel_join_v1_checks(token, channel_id)

    index = get_index(token)

    auth_user_id = store['user_id'][index]

    index = store['channel_id'].index(channel_id)
    store['channel_all_members'][index].append(auth_user_id)
    data_store.set(store)

    return {}

def channel_leave_v1_checks(token, channel_id):
    """
    Helper function for channel_leave_v1 to check for errors.
    Args:
        token (string): JWT of user session.
        channel_id (int): channel ID of channel being left.
    Exceptions:
        InputError: When channel_id does not refer to a valid channel.
        AccessError: When channel_id is valid but the authorised user is not
        a member of the channel.
    Returns:
        N/A.
    """
    store = data_store.get()

    # Raise InputError if channel doesn't exist.
    if channel_id not in store["channel_id"]:
        raise InputError(description = "Invalid channel ID")
    # Raise AccessError if token is invalid.
    token_found = 0
    for user_tokens in store["token"]:
        if token in user_tokens:
            token_found = 1
            break
    if token_found == 0:
        raise AccessError(description = "Invalid token")

    # Finding ID of user to be removed.
    user_index = get_index(token)

    auth_user_id = store["user_id"][user_index]

    channel_index = store["channel_id"].index(channel_id)

    # Raise AccessError if user is not a member of a valid channel.
    if channel_id in store["channel_id"] and auth_user_id not in store["channel_all_members"][channel_index]:
        raise AccessError(description = "Authorised user is not a member of the channel")

def channel_leave_v1(token, channel_id):
    """
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel.
    Their messages should remain in the channel. If the only channel owner leaves, the channel will remain.
    Parameters:
        - token (string): authorised users token
        - channel_id (int): ID of channel being left.
    Exceptions:
        - InputError when:
            - channel_id does not refer to a valid channel
        - AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel
    Returns: {} (empty dictionary)
    """
    channel_leave_v1_checks(token, channel_id) # Checking for errors.

    store = data_store.get()

    # Finding user ID of member to be removed.
    user_index = get_index(token)

    auth_user_id = store["user_id"][user_index]

    channel_index = store["channel_id"].index(channel_id)

    store["channel_all_members"][channel_index].remove(auth_user_id)

    data_store.set(store)
    return {}

def channel_addowner_v1_checks(token, channel_id, u_id):
    """
    Helper function for channel_addowner_v1 to check for errors.
    Args:
        token (string): token of user who is an owner.
        channel_id (int): ID of the channel that the user is to be made owner of.
        u_id (int): ID of user to be made an owner.
    Exceptions:
        InputError: When
            - channel_id does not refer to a valid channel.
            - u_id does not refer to a valid user.
            - u_id refers to a user who is not a member of the channel.
            - u_id refers to a user who is already an owner of the channel.
        AccessError: When
            - u_id refers to a user who is already an owner of the channel.
    Returns:
        N/A.
    """
    store = data_store.get()

    # Raise InputError if channel doesn't exist.
    if channel_id not in store["channel_id"]:
        raise InputError(description = "Invalid channel ID")
    # Raise InputError if user doesen't exist.
    if u_id not in store["user_id"]:
        raise InputError(description = "Invalid user ID")
    # Raise AccessError if token is invalid.
    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")

    # Finding token owner.
    user_index = get_index(token)

    auth_user_id = store["user_id"][user_index]

    channel_index = store["channel_id"].index(channel_id)

    # Raise InputError if user is not a member of the channel.
    if u_id not in store["channel_all_members"][channel_index]:
        raise InputError(description = "User is not a member of channel")
    # Raise InputError if user is already an owner of the channel.
    if u_id in store["channel_owner_members"][channel_index]:
        raise InputError(description = "User is already an owner of the channel")
    # Raise AccessError if token owner is not a member.
    if auth_user_id not in store["channel_all_members"][channel_index]:
        raise AccessError(description = "Token owner is not a channel member.")
    # Raise AccessError if authorised user does not have owner permissions.
    if auth_user_id not in store["channel_owner_members"][channel_index] and auth_user_id not in store["global_owners"]:
        raise AccessError(description = "Authorised user does not have owner permissions.")

def channel_addowner_v1(token, channel_id, u_id):
    """
    Make a user with ID 'u_id" an owner of the channel given that a user
    specified by a token is authorised as an owner.
    Args:
        token (string): token of user who is an owner.
        channel_id (int): ID of the channel that the user is to be made owner of.
        u_id (int): ID of user to be made an owner.
    Exceptions:
        InputError: When
            - channel_id does not refer to a valid channel.
            - u_id does not refer to a valid user.
            - u_id refers to a user who is not a member of the channel.
            - u_id refers to a user who is already an owner of the channel.
        AccessError: When
            - u_id refers to a user who is already an owner of the channel.
    Returns:
        {} (empty dict): If user is successfully made owner.
    """
    channel_addowner_v1_checks(token, channel_id, u_id) # Error checks.

    store = data_store.get()

    channel_index = store["channel_id"].index(channel_id)

    store["channel_owner_members"][channel_index].append(u_id)

    return {}

def channel_removeowner_v1_checks(token, channel_id, u_id):
    """
    Helper function for channel_removeowner_v1 to check for errors.
    Args:
        token (string): token of user who is an owner.
        channel_id (int): ID of the channel that the user is to be removed as owner from.
        u_id (int): ID of user to be removed as owner.
    Exceptions:
        InputError: When
            - channel_id does not refer to a valid channel.
            - u_id does not refer to a valid user.
            - u_id refers to a user who is not an owner of the channel.
            - u_id refers to a user who is currently the only owner of the channel.
        AccessError: When
            - channel_id is valid and authorised user does not have owner permissions.
    Returns:
        {} (empty dict): If user is successfully removed as owner.
    """
    store = data_store.get()

    # Raise InputError if channel doesn't exist.
    if channel_id not in store["channel_id"]:
        raise InputError(description = "Invalid channel ID.")
    # Raise InputError if user doesen't exist.
    if u_id not in store["user_id"]:
        raise InputError(description = "Invalid user ID.")
        
    # Raise AccessError if token is invalid.
    if any(token in i for i in store['token']) == False:
        raise AccessError(description = "AccessError: Invalid token")

    # Finding token owner.
    user_index = get_index(token)

    auth_user_id = store["user_id"][user_index]

    channel_index = store["channel_id"].index(channel_id)

    # Raise AccessError if token owner is not a member.
    if auth_user_id not in store["channel_all_members"][channel_index]:
        raise AccessError(description = "Token owner is not a channel member.")
    # Raise AccessError if authorised user does not have owner permissions.
    if auth_user_id not in store["channel_owner_members"][channel_index] and auth_user_id not in store["global_owners"]:
        raise AccessError(description = "Authorised user does not have owner permissions.")
    # Raise InputError if user is not an owner of the channel.
    if u_id not in store["channel_owner_members"][channel_index]:
        raise InputError(description = "User is not an owner of channel")
    # Raise InputError if user is only owner of the channel
    if u_id in store["channel_owner_members"][channel_index] and len(store["channel_owner_members"][channel_index]) == 1:
        raise InputError(description = "User is the only owner of the channel")

def channel_removeowner_v1(token, channel_id, u_id):
    """
    Remove a user with ID 'u_id" as owner of the channel given that a user
    specified by a token is authorised as an owner.
    Args:
        token (string): token of user who is an owner.
        channel_id (int): ID of the channel that the user is to be removed as owner from.
        u_id (int): ID of user to be removed as owner.
    Exceptions:
        InputError: When
            - channel_id does not refer to a valid channel.
            - u_id does not refer to a valid user.
            - u_id refers to a user who is not an owner of the channel.
            - u_id refers to a user who is currently the only owner of the channel.
        AccessError: When
            - channel_id is valid and authorised user does not have owner permissions.
    Returns:
        {} (empty dict): If user is successfully removed as owner.
    """
    channel_removeowner_v1_checks(token, channel_id, u_id)

    store = data_store.get()

    channel_index = store["channel_id"].index(channel_id)

    store["channel_owner_members"][channel_index].remove(u_id)

    return {}
