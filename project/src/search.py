from src.error import AccessError, InputError
from src.data_store import data_store
from src.other import get_index

def search_v1_error_checks(token, query_str):
    """
    Helper error checker function for search/v1.
    Args:
        - token (string): JWT of user.
        - query_str (string): Query string.
    Exceptions:
        - AccessError when:
            - Invalid token
        - InputError when:
            - query_str length < 1.
            - query_str length > 1000
    Returns:
        N/A.
    """
    store = data_store.get()

    # Raise InputError if query string length < 1 or > 1000.
    query_str_len = len(query_str)
    if query_str_len < 1 or query_str_len > 1000:
        raise InputError(description = "Invalid query string length.")

    # Raise AccessError if token is invalid.
    if not any(token in user_tokens for user_tokens in store["token"]):
        raise AccessError(description = "search/v1 -> Invalid Token")

def search_v1(token, query_str):
    """
    Given a query string, return a collection of messages in all
    of the channels/DMs that the user has joined that contain the
    query (case-insensitive). There is no expected order for these messages.
    Args:
        - token (string): JWT of user.
        - query_str (string): Query string.
    Exceptions:
        - AccessError when:
            - Invalid token
        - InputError when:
            - query_str length < 1.
            - query_str length > 1000
    Returns:
        - {messages}: List of dictionaries, where each dictionary contains types
        { message_id, u_id, message, time_sent, reacts, is_pinned  }
    """
    store = data_store.get()

    # Error checks.
    search_v1_error_checks(token, query_str)

    # Finding token owner.
    u_id = store["user_id"][get_index(token)]

    messages = []

    # Finding messages containing query_str in channels that user is a part of.
    for channel in store["channel_messages"]:
        ch_idx = store["channel_messages"].index(channel)
        for message in channel:
            if u_id in store["channel_all_members"][ch_idx] and query_str in message["message"]:
                messages.append(message)

    # Finding messages containing query_str in dms that user is a part of.
    for dm in store["dm_messages"]:
        dm_idx = store["dm_messages"].index(dm)
        for message in dm:
            if (u_id == store["dm_owner"][dm_idx] or u_id in store["dm"][dm_idx]) and query_str in message["message"]:
                messages.append(message)

    return {"messages": messages}