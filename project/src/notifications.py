from src.error import AccessError, InputError
from src.data_store import data_store
from src.other import get_index

def notifications_get_v1(token):
    """
    Return a user's most recent 20 notifications, ordered from most recent to least recent.
    Args:
        - token (string): user's token.
    Exceptions:
        - AccessError when:
            - token invalid.
    Returns:
        - {notifications} (list of dictionaries): dictionary is of type {channel_id, dm_id, notification_message}
            - channel_id (int): ID of channel notification event occured. -1 if it occured in a DM.
            - dm_id (int): ID of dm notification event occured. -1 if it occured in a channel.
            - notification_message (string): string of the follow formats for each action.
                -tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
                - reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
                - added to a channel/DM: "{User’s handle} added you to {channel/DM name}"
    """
    store = data_store.get()

    # Raise AccessError if token is invalid.
    if not any(token in user_tokens for user_tokens in store["token"]):
        raise AccessError(description = "notifications_get -> Invalid Token")
    
    u_index = get_index(token)
    reversed_notis = reversed(store["notifications"][u_index])
    notis = []
    notification_counter = 0
    for notification in reversed_notis:
        if notification_counter == 20:
            break
        notis.append(notification)
        notification_counter += 1

    return {"notifications": notis}