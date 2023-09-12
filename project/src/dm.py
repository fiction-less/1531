''' Implementation for dm.py
Written 18/03/22
by Ding Mingrui (z5292268@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import get_index


def dm_create_v1_check(token, u_ids):
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    if len(set(u_ids)) != len(u_ids):
        raise InputError(description = "InputError: Duplicate uid")
    for i in u_ids:
        if i not in store['user_id']:
            raise InputError(description = "InputError: Invalid user")


def dm_create_v1(token, u_ids):
    """
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. The creator is the owner of the DM.
    name should be automatically generated based on the users that are in this DM. The name should be an alphabetically-sorted,
    comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.
    Parameters:
        - token (string): authorised users token
        - u_ids (list): list of user_ids.
    Exceptions:
        - InputError when
            - any u_id in u_ids does not refer to a valid user
            - there are duplicate 'u_id's in u_ids
    Returns: {dm_id} if dm is successfully created.
        - dm_id (int): ID of created dm.
    """
    list_of_handle = []
    store = data_store.get()
    dm_create_v1_check(token, u_ids)
    index = get_index(token)

    for u_id in u_ids:
        index1 = store['user_id'].index(u_id)
        list_of_handle.append(store['handle'][index1])
    list_of_handle.append(store['handle'][index])
    list_of_handle.sort()
    str1 = ''
    for a in list_of_handle:
        str1 += a
        if a != list_of_handle[len(list_of_handle) - 1]:
            str1 += ', '
    store['dm_name'].append(str1)
    store['dm_owner'].append(store['user_id'][index])
    store['dm'].append(u_ids)
    store['dm_id_tracker'] += 1
    store['dm_messages'].append([])
    store['dm_id'].append(store['dm_id_tracker'])

    # Sending notification to user.
    dm_id = store["dm_id_tracker"]
    for u_id in u_ids:
        user_index = store["user_id"].index(u_id)
        user_handle = store["handle"][user_index]
        store["notifications"][user_index].append({
            "channel_id": -1,
            "dm_id": dm_id,
            "notification_message": f"{user_handle} added you to {str1}"
        })

    data_store.set(store)
    '''return {'a': store}'''
    return {'dm_id': store['dm_id_tracker']}


def dm_list_v1(token):
    """
    Returns the list of DMs that the user is a member of.
    Parameters:
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: {dms} if dm list is successfully retrieved.
        - dms (list): List of DMS that the user is a member of.
    """
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

    dms = []
    sd = store['user_id'][index]

    for i in range(0, len(store['dm'])):
        if store['dm_owner'][i] == sd:
            dms1 = {'dm_id': store['dm_id'][i], 'name': store['dm_name'][i]}
            dms.append(dms1)
        elif sd in store['dm'][i]:
            dms1 = {'dm_id': store['dm_id'][i], 'name': store['dm_name'][i]}
            dms.append(dms1)
    return {'dms': dms}


def dm_remove_v1(token, dm_id):
    """
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.
    Parameters:
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
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

    if dm_id not in store['dm_id'] or dm_id < 1:
        raise InputError(description = "InputError: Invalid dm_id")
    index1 = store['dm_id'].index(dm_id)
    if store['user_id'][index] != store['dm_owner'][index1]:
        raise AccessError(description = "AccessError: Is not the original DM creator")
    store['dm_name'].pop(index1)
    store['dm_owner'].pop(index1)
    store['dm'].pop(index1)
    store['dm_messages'].pop(index1)
    store['dm_id'].pop(index1)
    data_store.set(store)
    return {}


def dm_details_v1(token, dm_id):
    """
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.
    Parameters:
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
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

    if dm_id not in store['dm_id'] or dm_id < 1:
        raise InputError(description = "InputError: Invalid dm_id")
    index1 = store['dm_id'].index(dm_id)
    if store['user_id'][index] != store['dm_owner'][index1] and store['user_id'][index] not in store['dm'][index1]:
        if store['user_id'][index] not in store['global_owners']:
            raise AccessError(description = "AccessError: is not a member of the DM")
    asd = []
    for us in store['dm'][index1]:
        index5 = store['user_id'].index(us)
        dic = {'u_id': us,
               'email': store['email'][index5],
               'name_first': store['name_first'][index5],
               'name_last': store['name_last'][index5],
               'handle_str': store['handle'][index5]}
        asd.append(dic)
    owner_id = store['dm_owner'][index1]
    if owner_id == []:
        return {'name': store['dm_name'][index1],
                'members': asd}
    index4 = store['user_id'].index(owner_id)
    dic = {'u_id': owner_id,
           'email': store['email'][index4],
           'name_first': store['name_first'][index4],
           'name_last': store['name_last'][index4],
           'handle_str': store['handle'][index4]}
    asd.append(dic)
    return {'name': store['dm_name'][index1],
            'members': asd}


def dm_leave_v1(token, dm_id):
    """
    Given a DM ID, the user is removed as a member of this DM.
    The creator is allowed to leave and the DM will still exist if this happens. This does not update the name of the DM.
    Parameters:
        - token (string): users token
        - dm_id (int): ID of dm
    Exceptions:
        - InputError when:
            - dm_id does not refer to a valid DM
        - AccessError when:
            - dm_id is valid and the authorised user is not a member of the DM
    Returns:  {} (empty dictionary) if user successfully leaves dm.
    """
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

    if dm_id not in store['dm_id'] or dm_id < 1:
        raise InputError(description = "InputError: Invalid dm_id")
    index1 = store['dm_id'].index(dm_id)
    if store['user_id'][index] != store['dm_owner'][index1] and store['user_id'][index] not in store['dm'][index1]:
        raise AccessError(description = "AccessError: is not a member of the DM")
    if store['user_id'][index] == store['dm_owner'][index1]:
        store['dm_owner'][index1] = []
        '''store['user_id'][index] in store['dm'][index1]'''
    else:
        store['dm'][index1].remove(store['user_id'][index])
    data_store.set(store)
    return {}


def dm_messages_v1(token, dm_id, start):
    """
    Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50".
     Message with index 0 is the most recent message in the DM. This function returns a new index "end" which is the value of
    "start + 50", or, if this function has returned the least recent messages in the DM, returns -1 in "end" to indicate there are no
    more messages to load after this return.
    Parameters:
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
    store = data_store.get()

    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
    else:
        index = get_index(token)

    if dm_id not in store['dm_id'] or dm_id < 1:
        raise InputError(description = "InputError: Invalid dm_id")

    index1 = store['dm_id'].index(dm_id)

    if store['user_id'][index] != store['dm_owner'][index1] and \
            store['user_id'][index] not in store['dm'][index1]:
        raise AccessError(description = "AccessError: Is not a member of the DM")
    if len(store["dm_messages"][index1]) < start or start < 0:
        raise InputError(description = "InputError: Over total")
    if len(store["dm_messages"][index1]) == 0:
        return {'messages': [], 'start': 0, 'end': -1}


    return_messages = []
    end = start + 50
    if len(store["dm_messages"][index1]) - 1 <= end:
        store['dm_messages'][index1].reverse()
        i = start
        while i < len(store["dm_messages"][index1]):
            return_messages.append(store['dm_messages'][index1][i])
            i += 1
        end = -1
        store['dm_messages'][index1].reverse()
    # returns 50 messages, newest to oldest
    else:
        i = end - 1
        while i >= start:
            return_messages.append(store['dm_messages'][index1][i])
            i -= 1
    return {'messages': return_messages, 'start': start, 'end': end}
