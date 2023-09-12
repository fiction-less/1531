'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'email': [],
    'password': [],
    'name_first': [],
    'name_last': [],
    'handle': [],
    'profile_img_url': [],
    'token': [],                # list within list of tokens per user
    'dm': [],                   # [[2 ,3],[5, 6],[7, 8]]no owner id number, list of all uids for each dm
    'dm_name': [],              # ['asdsa, dsdsd','dasdasd, dasdasdas']
    'dm_owner': [],             # [1, 2, 3]
    'dm_id_tracker': 0,
    'dm_messages': [],          # [["sdsdsdsdsd", "dsdsdsdsdsd"]
    'dm_id': [],                # [1, 2, 3, 4]
    'session_id': 0,
    'user_id': [],
    'user_id_tracker': 0,
    'channel_name': [],
    'channel_owner_members': [],      #list within list of owner_members user_id eg [[1, 2], [3]]
    'channel_all_members': [],        #list within list of all_members user_id eg [[1, 2, 4], [3, 5]]
    'channel_is_public': [],
    'channel_messages': [],      # list within list of messages dict {message_id, u_id, message, time_sent, react, is_pinned}
    'channel_id': [],
    'channel_buffered_messages': [],# list within list of messages [message_id, u_id, message, time_sent ]
    'channel_standup': [],
    'channel_id_tracker': 0,
    'message_id_tracker': 0,
    'reset_code': [],
    'reset_code_tracker': 0,
    'global_owners': [],        # list of owner_users ( only 1 dm owner allowed)  and anyone else he grants permission to
    'removed_users': [],        # List of removed users from seams.
    'notifications': []         # List within list of dictionaries of notifications for each user[{channel_id, dm_id, notification_message}]
                                # channel_id == -1 if event (tags, reacts, adding to channel/dm) occured in dm, vice versa. User indexed.
}

## YOU SHOULD MODIFY THIS OBJECT ABOVE

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
