''' Implementation of users functions
Written 21/03/22
by Alyssa Lubrano (z5362292@ad.unsw.edu.au)
for COMP1531 Major Project '''

from src.data_store import data_store
from src.error import AccessError, InputError

def users_all_v1(token):
    """
    Returns a list of all users and their associated details.
    Parameters:
        - token (string): authorised users token.
    Exceptions:
        - N/A
    Returns: {users} if list of users and details retrieved.
        - users (list of dictionaries): List of dictionaries, where each dictionary contains types of user
    """
    store = data_store.get()
    
    if not any(token in row for row in store['token']):
        raise AccessError(description = "AccessError: Invalid token")
        
    users = {'users': []}
    
    for index in range(0, len(store['user_id'])):
        if store["user_id"][index] in store["removed_users"]: # Need this for admin/user/remove/v1
            continue
        data = {"u_id": store['user_id'][index], "email": store['email'][index],
        "name_first": store['name_first'][index], "name_last": store['name_last'][index],
        "handle_str": store['handle'][index], "profile_img_url": store['profile_img_url'][index]}
        users['users'].append(data)
    
    return users

