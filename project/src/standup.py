''' Implementation for standup.py
Written 9/04/22
by Ding Mingrui (z5292268@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import get_index
import threading
import time
from src.message import message_send_v1
def timeover(index1, token):
    store = data_store.get()
    channel_id = store['channel_id'][index1]
    if store['channel_buffered_messages'][index1] != []:
        message_send_v1(token, channel_id, store['channel_buffered_messages'][index1])
    store['channel_standup'][index1] = []
    store['channel_buffered_messages'][index1] = []
    data_store.set(store)
def standup_start_v1(token, channel_id, length):
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError("AccessError: Invalid token")
    else:
        index = get_index(token)
    userid = store['user_id'][index]
    if channel_id not in store['channel_id']:
        raise InputError("InputError: Invalid channel ID.")
    if length < 0:
        raise InputError("InputError: Length is a negative integer.")
    index1 = store['channel_id'].index(channel_id)
    if store['channel_standup'][index1] != []:
        raise InputError("InputError: An active standup is currently running.")
    if userid not in store['channel_all_members'][index1]:
        raise AccessError("AccessError: Not a member of the channel")
    #return {'a': store}
    t = threading.Timer(length, timeover, (index1, token))
    t.start()
    timestape = int(time.time())
    finish = timestape + length
    store['channel_standup'][index1] = finish
    data_store.set(store)
    return {'time_finish': finish}
def standup_active_v1(token, channel_id):
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError("AccessError: Invalid token")
    else:
        index = get_index(token)
    userid = store['user_id'][index]
    if channel_id not in store['channel_id']:
        raise InputError("InputError: Invalid channel ID.")
    index1 = store['channel_id'].index(channel_id)
    if userid not in store['channel_all_members'][index1]:
        raise AccessError("AccessError: Not a member of the channel")
    if store['channel_standup'][index1] == []:
        return{'is_active': False, 'time_finish': None}
    else:
        return{'is_active': True, 'time_finish': store['channel_standup'][index1]}
def standup_send_v1(token, channel_id, message):
    store = data_store.get()
    if not any(token in row for row in store['token']):
        raise AccessError("AccessError: Invalid token")
    else:
        index = get_index(token)
    userid = store['user_id'][index]
    if channel_id not in store['channel_id']:
        raise InputError("InputError: Invalid channel ID.")
    index1 = store['channel_id'].index(channel_id)
    if userid not in store['channel_all_members'][index1]:
        raise AccessError("AccessError: Not a member of the channel")
    if store['channel_standup'][index1] == []:
        raise InputError("InputError: An active standup is not currently running.")
    if len(message) > 1000:
        raise InputError("InputError: Length of message is over 1000 characters.")
    if store['channel_buffered_messages'][index1] == []:
        store['channel_buffered_messages'][index1].append(f"{store['handle'][index]}: {message}")
    else:
        store['channel_buffered_messages'][index1].append(f"\n{store['handle'][index]}: {message}")
    data_store.set(store)
    return{}








