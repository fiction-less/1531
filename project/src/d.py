"""
import re
message = "@kelly there you  Hello yoyog,@momdad,@mommy@mommy, are@james. hikellyb@jamiel,hii@Carsl,"
#

handles = list(filter(lambda word: "@" in word, message.split(" ")))

# split the message into words and filter words those with an @
# from the words trim everything before the first @ and split the word by if there is more than 1 tag
# trim anything after the first nonalpha numeric symbol

#gets all the possible tags into a list


handle_list = []
for handle in handles:

    i = handle.index('@')
    handle = handle[i+1:]

    if '@' in handle:
        handle = handle.split("@")

    if type(handle) != list:
        handle = handle.split(" ")
    handle_list.append(handle)
    flat_list = [item for sublist in handle_list for item in sublist]


handle_list = []
# cleans up the tags to get the handles
for handle in flat_list:
    if handle.isalnum() == True:
        handle=handle
    else :
        temp = re.search(r'\W+', handle[1:]).start()
        handle = handle[: temp+1]

    if handle not in handle_list:
        handle_list.append(handle)




"""
'''import time
import threading

def hello (num, num1=None):
    print(num1)
    sum = num + num1
    print("hello")
    print(sum)


print(time.time())
print(time.time() + 1)
time1 = ((time.time() + 3) - time.time())
send_message = threading.Timer(time1, hello,[1,2])
send_message.start()
time.sleep(3.1)

print("waiting")
'''
user_handle = "kelly"
msg = "Hello yoyog,@momdad,@momdad hikellyb@jamiel,hii@kellyb"
if f"@{user_handle}" in msg:
    print("hello")
    print(user_handle)