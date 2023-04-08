from src.data_store import data_store
from src.helpers import search_user_token
from src.error import AccessError

def get_notifications(token):
    '''
    Function Description:
        Return the user's most recent 20 notifications, ordered from most recent
        to least recent.

    Arguments:
        token (str)           - authorised user's hash

    Exceptions:
        AccessError           - Occurs when token is invalid

    Return Value:
        {notifications} on valid token
    '''

    store = data_store.get()

    # Check if token is valid, if it is get user dict
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='Token is invalid')

    # Get a copy of the user's notifications
    notifications = user['notifications'].copy()

    # Reverse the notifications such that they are sorted by most recent
    notifications.reverse()

    # If there are over 20 notifications, cut list down to first 20
    if len(notifications) > 20:
        notifications = notifications[0:20]
   
    return {'notifications': notifications}
