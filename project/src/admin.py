from src.error import AccessError, InputError
from src.data_store import data_store
from src.other import get_index

def admin_user_remove_v1_checks(token, u_id):
    """
    Helper function for admin_user_remove_v1 to check for errors.
        - token (string): JWT of global owner.
        - u_id (int): ID of user to be removed.
    Exceptions:
        - InputError. Occurs when:
            - 'u_id' does not refer to a valid user.
            - 'u_id' refers to a user who is the only global owner.
        - AccessError. Occurs when:
            - authorised user with JWT 'token' is not a global owner.
    Returns:
        - Nothing.
    """
    store = data_store.get()

    # Finding token owner.
    user_index = get_index(token)
    
    auth_user_id = store["user_id"][user_index]
    
    # Raise AccessError if token owner is unauthorised.
    if auth_user_id not in store["global_owners"]:
        raise AccessError(description = "admin_user_remove_v1 -> Unauthorised access. Token owner is not a global owner.")

    # Raise InputError if user does not exist.
    if u_id not in store["user_id"]:
        raise InputError(description = "admin_user_remove_v1 -> u_id invalid. Invalid user")
    # Raise input error if user is only global owner
    if u_id in store["global_owners"] and len(store["global_owners"]) == 1:
        raise InputError(description = "admin_user_remove_v1 -> User is the only global owner")

def admin_user_remove_v1(token, u_id):
    """
    As a global owner, remove user with ID 'u_id' from seams, including all dms and channels.
    Args:
        - token (string): JWT of global owner.
        - u_id (int): ID of user to be removed.
    Exceptions:
        - InputError. Occurs when:
            - 'u_id' does not refer to a valid user.
            - 'u_id' refers to a user who is the only global owner.
        - AccessError. Occurs when:
            - authorised user with JWT 'token' is not a global owner.
    Returns:
        - {} (empty dict): When user is removed from seams.
    """
    admin_user_remove_v1_checks(token, u_id) # Error checks.
    store = data_store.get()

    # Finding ID of user with token.
    user_index = get_index(token)

    user_index = store["user_id"].index(u_id) # Finding index in data store of user to be removed.

    # Removing user from seams.
    store["email"][user_index] = None
    store["password"][user_index] = None
    store["name_first"][user_index] = "Removed"
    store["name_last"][user_index] = "user"
    store["handle"][user_index] = None
    store["token"][user_index] = []
    # store["token"].pop(user_index)
    for dm in store["dm"]:
        if u_id in dm:
            dm.remove(u_id)
    if u_id in store["dm_owner"]:
        store["dm_owner"].remove(u_id)
    for owners in store["channel_owner_members"]:
        if u_id in owners:
            owners.remove(u_id)
    for members in store["channel_all_members"]:
        if u_id in members:
            members.remove(u_id)
    for channel in store["channel_messages"]:
        for message in channel:
            if message["u_id"] == u_id:
                message["message"] = "Removed user"
    if u_id in store["global_owners"]:
        store["global_owners"].remove(u_id)
    store["removed_users"].append(u_id)
    store["notifications"][user_index] = []
    return {}

def admin_userpermission_change_v1_errorChecks(token, u_id, permission_id):
    """
    Helper function for admin_userpermission_change_v1() to check for errors.
    Args:
        - token (string): JWT of authorised global owner/admin who is changing permissions.
        - u_id (int): User ID of user who is having their permissions change.
        - permission_id (int): ID of permission to be changed to. Either;
            - 1 (global owner).
            - 2 (member).
    Exceptions:
        - InputError when;
            - u_id does not refer to a valid user.
            - u_id refers to a user who is the only global owner and they are being demoted to a member.
            - permission_id invalid.
            - user already has permissions level of permission_id
        - AccessError when;
            - authorised user with token is not a global owner.
    Returns:
        - N/A
    """
    store = data_store.get()

    # Finding token owner.
    user_index = get_index(token)
    auth_user_id = store["user_id"][user_index]

    # Raise AccessError if authorised user is not a global owner.
    if auth_user_id not in store["global_owners"]:
        raise AccessError(description = "admin_userpermission_change_v1 -> authorised user with token is not a global owner")
       
    # Raise InputError if u_id does not refer to a valid user.
    if u_id not in store["user_id"]:
        raise InputError(description = "admin_userpermission_change_v1 -> u_id does not refer to a valid user.")
    # Raise InputError if u_id refers to a user who is the only global owner and they are being demoted to a member.
    if u_id in store["global_owners"] and len(store["global_owners"]) == 1 and permission_id == 2:
        raise InputError(description = "admin_userpermission_change_v1 -> user is only global owner")
    # Raise InputError if permission_id invalid.
    if permission_id != 1 and permission_id != 2:
        raise InputError(description = "admin_userpermission_change_v1 -> permission_id invalid")
    # Raise InputError if user already has permissions of permission_id
    if (permission_id == 1 and u_id in store["global_owners"]) or (permission_id == 2 and u_id not in store["global_owners"]):
        raise InputError(description = "admin_userpermission_change_v1 -> user already has permissions")

def admin_userpermission_change_v1(token, u_id, permission_id):
    """
    Given a user by their user ID, set their permissions to new permissions described by 'permission_id'.
    Args:
        - token (string): JWT of authorised global owner/admin who is changing permissions.
        - u_id (int): User ID of user who is having their permissions change.
        - permission_id (int): ID of permission to be changed to. Either;
            - 1 (global owner).
            - 2 (member).
    Exceptions:
        - InputError when;
            - u_id does not refer to a valid user.
            - u_id refers to a user who is the only global owner and they are being demoted to a member.
            - permission_id invalid.
            - user already has permissions level of permission_id
        - AccessError when;
            - authorised user with token is not a global owner.
    Returns:
        - {} (empty dict). When permission_id successfully changed.
    """
    admin_userpermission_change_v1_errorChecks(token, u_id, permission_id)
    store = data_store.get()

    if permission_id == 1:
        store["global_owners"].append(u_id)
    if permission_id == 2:
        store["global_owners"].remove(u_id)

    return {}


