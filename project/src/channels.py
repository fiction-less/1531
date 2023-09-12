''' Implementation of channels functions
Written 27/02/22
by Aryan Bahinipati (z5310696@ad.unsw.edu.au) and Alyssa Lubrano (z5362292@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import get_index

def channels_list_v1(token):
    """
    Provide a list of all channels (and their associated details) that the authorised user is part of.
    Parameters: 
        - token (string): Authorised users token.
    Exceptions:
        - N/A
    Returns: { channels }
        - channels (List of dictionaries, where each dictionary contains types { channel_id, name }): list of channels authorised user is a part of.
    """

    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")

    index = get_index(token)

    auth_user_id = store['user_id'][index]

    channels = {'channels': []}

    for i in range(0, len(store['channel_id'])):
        if auth_user_id in store['channel_all_members'][i]:
            data = {'channel_id': store['channel_id'][i], 'name': store['channel_name'][i]}
            channels['channels'].append(data)

    return channels

def channels_listall_v1(token):
    """
    Provide a list of all channels, including private channels, (and their associated details).
    Parameters: 
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: { channels }
        - channels (List of dictionaries, where each dictionary contains types { channel_id, name }): list of channels authorised user is a part of.
    """

    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")

    channels = {'channels': []}

    for i in range(0, len(store['channel_id'])):
        data = {'channel_id': store['channel_id'][i], 'name': store['channel_name'][i]}
        channels['channels'].append(data)

    return channels

def channels_create_v1(token, name, is_public):
    """
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

    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid Token")
    elif len(name) < 1 or len(name) > 20:
        raise InputError(description = "InputError: The channel name must be between 1 and 20 characters")

    index = get_index(token)

    auth_user_id = store['user_id'][index]
    
    store['channel_buffered_messages'].append([])
    store['channel_standup'].append([])
    store['channel_name'].append(name)
    store['channel_owner_members'].append([auth_user_id])
    store['channel_all_members'].append([auth_user_id])
    store['channel_is_public'].append(is_public)
    store['channel_id_tracker'] += 1
    store['channel_id'].append(store['channel_id_tracker'])
    ##
    store['channel_messages'].append([])
    ##
    data_store.set(store)

    return {"channel_id": store['channel_id_tracker']}

