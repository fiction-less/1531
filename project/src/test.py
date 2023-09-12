'''
import re
message = "@tracy@veronics, . how are you doing?? love you @rylue. lover @monra@roman"

handles = list(filter(lambda word: "@" in word, message.split(" ")))

for idx, i in enumerate(handles):
    if i[:-1].isalnum() == False:
        handles[idx] = i[:-1]


print("handle",handles)

handle_list = []
for handle in handles:
    handle = handle.split('@')
    for i in handle:
        if i != '':
            handle_list.append(i)

print(handle_list)

print(handle_list)
'''




from src.data_store import data_store
from src.auth import auth_register_v1
from src.auth import auth_register_v1
from src.dm import dm_create_v1, dm_leave_v1, dm_details_v1, dm_messages_v1, dm_remove_v1
from src.message import message_edit_v1, message_send_dm_v1, message_send_v1
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1

clear_v1()
store = data_store.get()

user = auth_register_v1("aryj1@yahoo.com", "a123456", "Aryan", "Bahinipati")
user1 = auth_register_v1("asdfgjdjfkgshjk1@yahoo.com", "a123456", "mom", "dad")
user2 = auth_register_v1("aryj1s@yahoo.com", "a123456", "kelly", "B")
user3 = auth_register_v1("asdfkgshjk1@yahoo.com", "a123456", "jamie", "L")


token = user['token']
token1 = user1['token']

uid = user['auth_user_id']
uid1 = user1['auth_user_id']

channel = channels_create_v1(token1, "YOLO", True)
channel_id = channel['channel_id']

print(store['handle'])

mess = message_send_v1(token1, channel_id, "Hello yoyog,@momdad,@momdad hikellyb@jamiel,hii@kellyb")
message_send_v1(token1, channel_id, "jeepers,@momdad")
print(store['notifications'])

"""
dm = dm_create_v1(token, uids)
dm_id = dm['dm_id']
mess = message_send_dm_v1(token, dm_id, "Hello")
message_id = mess['message_id']

print(message_id)

print(store['dm_messages'][0][0])
pin = message_pin_v1(token, message_id)
print(store['dm_messages'][0][0])
message_pin_v1(token, message_id)
"""