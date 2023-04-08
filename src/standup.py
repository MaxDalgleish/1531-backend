'''
standup.py implementation

    Description:
        Implementations of standup functions

    Functions:
        - Main functions:
            - standup_start(token, channel_id, length)
            - startup_active(token, channel_id)
            - standup_send(token, channel_id, message)

        - Helper functions:
            - standup_found(channel_id, store)
            - end_message(user, channel_id, channel, store)

'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import search_user_token, is_channel_valid, get_channel, \
                        is_a_member, update_user_stat_message, \
                        update_workspace_message
from .message import get_new_message_id
from datetime import datetime, timedelta
import time
import threading


# Check for existing standups
def standup_found(channel_id, store):
    '''
    Function Description:
        Finds the standup for the given channel

    Arguments:
        channel_id (int)        - id of the channel
        store                   - data store

    Exceptions:
        None

    Return Value:
        Returns channel, if found
    '''

    for channel in store['standups']:
        if channel_id == channel['channel_id']:
            return channel

    return None

def standup_start(token, channel_id, length):
    '''
    Function Description:
        Start a standup in the given channel

    Arguments:
        token (str)             - authorisation hash
        channel_id (int)        - id of the channel
        length (int)            - duration of standup

    Exceptions:
        InputError              - Channel id doesn't refer to a valid channel
                                - Length is a negative integer
                                - Active standup is alreay running

        AccessError             - Occurs when Token is invalid
                                - when channel_id is valid and the authorised user is
                                not in the channel

    Return Value:
        Returns {time_finish}
    '''

    store = data_store.get()
    
    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check that length is positive
    if length < 1:
        raise InputError(description='Length must be positive')

    # Check if channel_id is valid
    if is_channel_valid(channel_id, store) is False:
        raise InputError(description='Invalid channel_id')

    # Check if there is an existing standup already
    if standup_found(channel_id, store) is not None:
        raise InputError(description='A standup is already active')
    
    # Get channel dictionary
    channel = get_channel(channel_id, store)

    # Check if user is a member of the channel
    if is_a_member(user['u_id'], channel) is False:
        raise AccessError(description='You are not a member of this channel')

    # Calculate standup ending time, as a unix time stamp
    time_finish = datetime.now() + timedelta(seconds=length)
    time_finish = int(time_finish.timestamp())

    # Start the thread
    t = threading.Timer(length, end_message, args=(user, channel_id, channel, store))

    t.start()

    # Creates a temporary dict to store incoming standup messages
    standup_dict = { 'channel_id': channel_id,
                     'creator_id': user['u_id'],
                     'time_finish': time_finish,
                     'messages': []}

    store['standups'].append(standup_dict)

    data_store.set(store)

    return {'time_finish': time_finish}


def standup_active(token, channel_id):
    '''
    Function Description:
        Check if a standup is active

    Arguments:
        token (str)             - authorisation hash
        channel_id (int)        - id of the channel

    Exceptions:
        InputError              - Channel id doesn't refer to a valid channel

        AccessError             - Occurs when Token is invalid
                                - when channel_id is valid and the authorised user is
                                not in the channel

    Return Value:
        Returns {is_active, time_finish}
    '''
    
    store = data_store.get()
    
    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if channel_id is valid
    if is_channel_valid(channel_id, store) is False:
        raise InputError(description='Invalid channel_id')
    
    # Get channel dictionary
    channel = get_channel(channel_id, store)

    # Check if user is a member of the channel
    if is_a_member(user['u_id'], channel) is False:
        raise AccessError(description='You are not a member of this channel')

    # Check if there is an existing standup already
    standup_channel = standup_found(channel_id, store)

    # Returns false if no active standup
    if standup_channel is None:
        return {'is_active': False,
                'time_finish': None}

    # Return True, with ending time of standup
    end_time = standup_channel['time_finish']

    return {'is_active': True,
            'time_finish': end_time}
    
    
def standup_send(token, channel_id, message):
    '''
    Function Description:
        Sends a message which gets buffered to the queue. Adds all the standup messages
        into the message dict after standup is over

    Arguments:
        token (str)             - authorisation hash
        channel_id (int)        - id of the channel
        message (str)           - message

    Exceptions:
        InputError              - Channel id doesn't refer to a valid channel
                                - Length of message over 1000 chars
                                - No active standup is alreay running

        AccessError             - Occurs when Token is invalid
                                - when channel_id is valid and the authorised user is
                                not in the channel

    Return Value:
        Returns {}
    '''

    store = data_store.get()
    
    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check that length is positive
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Length must be less than 1000 characters')

    # Check if channel_id is valid
    if is_channel_valid(channel_id, store) is False:
        raise InputError(description='Invalid channel_id')
    
    # Get channel dictionary
    channel = get_channel(channel_id, store)

    # Check if user is a member of the channel
    if is_a_member(user['u_id'], channel) is False:
        raise AccessError(description='You are not a member of this channel')

    # Check if there is an existing standup already
    standup_curr = standup_found(channel_id, store)
    if standup_curr is None:
        raise InputError(description='A standup is not currently active')

    # Creates new message and appends it to the temporary dictionary
    new_message = {'user_handle': user['handle_str'],
                   'message': message}

    standup_curr['messages'].append(new_message)

    data_store.set(store)
    return {}


def end_message(user, channel_id, channel, store):
    '''
    Function Description:
        Collects the standup messages and sends it to the channel
        Deletes the temporary standup dict

    Arguments:
        user                    - user
        channel_id (int)        - id of the channel
        channel                 - channel being used
        store                   - duration of standup

    Exceptions:
        None

    Return Value:
        None
    '''
    
    temp_standup = standup_found(channel_id, store)

    # Should only return if pytest clears the dict
    if temp_standup is None:
        return
    
    # Create the new message, which would be added to the channel messages
    new_message = ''
    for message in temp_standup['messages']:
        temp_message = (f"{message['user_handle']}: {message['message']}\n")
        new_message += temp_message

    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}

    # Creates the new message for channel_messages
    message_dict = {'message_id': get_new_message_id(store),
                    'u_id': temp_standup['creator_id'],
                    'message': new_message,
                    'time_created': temp_standup['time_finish'],
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'channel_id': channel_id}

    # Append the message
    store['messages'].append(message_dict)
    channel['messages'].append(message_dict)
    
    update_user_stat_message(user, store)
    update_workspace_message(user, store)

    # Delete temporary standup dict
    store['standups'].remove(temp_standup)

    data_store.set(store)
    return
