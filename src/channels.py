'''
channels.py implementation

    Functions:

    - channels_list_v1(token)
    - channels_listall_v1(token)
    - channels_create_v1(token, name, is_public)
'''

from src.error import AccessError, InputError
from src.data_store import data_store
from src.helpers import search_user_token, \
                        update_user_stat_channel, \
                        update_workspace_stat_channel

def channels_list_v1(token):

    '''
    Function Description:
        Provide a list of all channels (and their associated details) that the
        authorised user is part of.

    Arguments:
        token (string)      - User's token

    Exceptions:
        AccessError         - Occurs when token is invalid

    Return Value:
        Returns {channels} on: valid token
    '''

    store = data_store.get()
    # Find the user givne the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description='TOKEN INVALID')

    # Create an empty list to return
    return_list = []

    # Loop through the channels in data_store
    for channel in store['channels']:

        # Loop through the members in each channel
        for member in channel['all_members']:

            # If the auth_user's id is found in all_members
            if member['u_id'] == found_user['u_id']:

                # Append the a dictionary that includes channel_id and name
                # to the list of channels that the user is a member in
                return_list.append({'channel_id':channel['channel_id'],
                                    'name': channel['name']})

    return {
        'channels': return_list
    }

def channels_listall_v1(token):

    '''
    Function Description:
        Provide a list of all channels, including private channels, and their
        associated details

    Arguments:
        token (string)      - User's token

    Exceptions:
        AccessError         - Occurs when token is invalid

    Return Value:
        Returns {channels} on: valid token
    '''

    store = data_store.get()
    # Find the user givne the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description='TOKEN INVALID')

    return_all = []
    # Loop through the channels
    for channel in store["channels"]:
        # Append dictionary with channel_id and name to return_all list
        return_all.append({'channel_id': channel['channel_id'],
                                'name': channel['name']})

    # List of all channels and associate info is returned
    return {"channels": return_all}

def channels_create_v1(token, name, is_public):

    '''
    Function Description:
        Creates a new channel with the given name that is either a public or
        private channel and user who created it automatically joins the channel.

    Arguments:
        token (string)      - token of the user
        name (string)               - channel name
        is_public (boolean)         - public or private

    Exceptions:
        InputError  - Occurs when length of name is less than 1 or more than 20
                    characters
        AccessError - Occurs when token is invalid

    Return Value:
        Returns {channel_id} on: valid token, channel name and public/private
        status
    '''

    store = data_store.get()
    # Find the user given the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description='TOKEN INVALID')

    # If channel name didn't have a length between 0 to 20, raise inputerror
    if name == "" or len(name) > 20:
        raise InputError("Please enter a valid channel name")

    # The channel id is created from the length of the elements in storage plus one
    channel_id = len(store['channels']) + 1

    # Creating a dictionary for the user data to be added to the channel
    for person in store['users']:
        # If matching user is found set user as that individual and break
        if person['u_id'] == found_user['u_id']:
            user = {'u_id': found_user['u_id'],
                    'email': person['email'],
                    'name_first': person['name_first'],
                    'name_last': person['name_last'],
                    'handle_str': person['handle_str'],
                    'profile_img_url': person['profile_img_url']}

    # The valid information is appended to the list
    store['channels'].append({'channel_id': channel_id, 'name': name,
                              'is_public': is_public, 'owner_members': [user],
                              'all_members': [user], 'messages': []})
    
    update_user_stat_channel(found_user, store)
    update_workspace_stat_channel(found_user, store)

    # Set data to datastore
    data_store.set(store)

    # Returning the channel_id of the created channel
    return {
        'channel_id': channel_id
    }
