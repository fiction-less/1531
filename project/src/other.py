# # Implementation of other functions
# Written 28/02/22
# by Daniel Wang (z5312741@ad.unsw.edu.au)
# for COMP1531 Major Project

from src.data_store import data_store

import os
import glob
import shutil

def clear_v1():
    """
    Resets the internal data of the application to its initial state.
    Parameters:  {}
        - N/A
    Exceptions:
        - N/A
    Returns: {}
        - {} (dictionary): Empty dict.
    """

    store = data_store.get()

    store['email'] = []
    store['password'] = []
    store['name_first'] = []
    store['name_last'] = []
    store['handle'] = []
    store['profile_img_url'] = []
    store['token'] = []
    store['session_id'] = 0
    store['user_id'] = []
    store['user_id_tracker'] = 0
    store['channel_name'] = []
    store['channel_owner_members'] = []
    store['channel_all_members'] = []
    store['channel_is_public'] = []
    store['channel_messages'] = []
    store['channel_buffered_messages'] = []
    store['channel_standup'] = []
    store['channel_id'] = []
    store['channel_id_tracker'] = 0
    store['message_id_tracker']= 0
    store['dm'] = []
    store['dm_name'] = []
    store['dm_id_tracker'] = 0
    store['dm_messages'] = []
    store['dm_owner'] = []
    store['dm_id'] = []
    store['global_owners'] = []
    store['removed_users'] = []
    store['reset_code'] = []
    store['reset_code_tracker'] = 0
    store["notifications"] = []
    data_store.set(store)

    # Clears imgurl file and just keeps default.jpg

    files = glob.glob(f'{os.getcwd()}/imgurl/*')

    for f in files:
        os.remove(f)

    src_path = f"{os.getcwd()}/default.jpg"
    dst_path = f"{os.getcwd()}/imgurl/default.jpg"

    shutil.copyfile(src_path, dst_path)

    return {}

def get_index(token):
    index = 0

    store = data_store.get()

    for index in range(0, len(store['token'])):
        if token in store['token'][index]:
            break

    return index

