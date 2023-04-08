'''
search.py implementation

    Description:
        Implementations of search functions

    Functions:
        - Main functions:
            - search(token, query_str)
        - Helper functions:
            - channel_messages_query(user, query_str)
            - dm_messages_query(user, query_str)

'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import search_user_token, is_a_member, is_a_member_dm

def search(token, query_str):
    '''
    Function Description:
        Given a query string, return a collection of messages in all of the channel/dm's that the user has joined that contain the query.

    Arguments:
        token (str)                 - authorisation hash
        query_str (str)             - string being searched

    Exceptions:
        AccessError     - When token is invalid
        InputError      - When length of query_str is less than 1 or over 1000 characters

    Return Value:
        Returns True on: user in channel is found
        Returns False on: user in channel is not found
    '''

    store = data_store.get()

    # Check if user token is valid
    found_user = search_user_token(token, store['users'])
    if found_user is None:
        raise AccessError(description='TOKEN INVALID')

    # Raise an InputError if query_str is over 1000 characters
    if len(query_str) > 1000:
        raise InputError(description='The query cannot be over 1000 characters in length')
            
    # Raise an InputError if query_str is empty
    elif len(query_str) == 0:
        raise InputError(description='The query cannot be empty')

    # return list containing all the message dictionaries that the substring is part of
    return_list = []

    # Checking all the channels that have been created for the query_str
    return_list = channel_messages_query(found_user, query_str)

    # Checking all of the dms that have been created for the query_str
    return_list.extend(dm_messages_query(found_user, query_str))

    # Returning the list of messages that the query_str is a part of
    return {'messages': return_list}

# Function to return a list of messages that query_str is a substring of in channels
def channel_messages_query(user, query_str):
    store = data_store.get()
    list = []

    # Checking all the channels that have been created
    for channel in store['channels']:
        # Checking if the user is a member of the channel
        if is_a_member(user['u_id'], channel) is True:
            # Searching all the messages that have been sent in the channel
            for message in channel['messages']:
                # Checking if the query_str is a subtring of the message
                if query_str in message['message']:
                    list.append(message)
    return list

# Function to return a list of messages that query_str is a substring of in dms
def dm_messages_query(user, query_str):
    store = data_store.get()
    list = []

    # Checking all of the dms that have been created
    for dm in store['dms']:
        # Checking if the user is a member of the dm
        if is_a_member_dm(user['u_id'], dm['members']):
            # Searching all of the messages that have been sent in the dm
            for message in dm['messages']:
                # Checking if the query_str is a substring of the message
                if query_str in message['message']:
                    list.append(message)
    return list

