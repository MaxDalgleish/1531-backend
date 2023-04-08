'''
channel.py implementation

    Functions:

    - search_channel_id(channel_id, store)
    - is_a_member(channel, temp_id)
    - is_channel_owner(channel_id, u_id)
    - add_user(u_id, channel_id, store)
    - channel_invite_v1(auth_user_id, channel_id, u_id)
    - channel_details_v1(auth_user_id, channel_id)
    - channel_messages_v1(auth_user_id, channel_id, start)
    - cant_access(channel_id, store)
    - global_owner(auth_user_id, store)
    - channel_join_v1(auth_user_id, channel_id)
    - channel_addowner(token, channel_id, u_id)
    - channel_removeowner(token, channel_id, u_id)
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import search_user_token, \
                        is_a_valid_uid, \
                        send_notification, \
                        update_user_stat_channel, \
                        change_is_this_user_reacted

def search_channel_id(channel_id, store):

    '''
    Function Description:
        Given a channel id and storage, checks if the channel exists.

    Arguments:
        channel_id (integer)        - channel id number
        store (data)                - data storage

    Exceptions:
        N/A

    Return Value:
        Returns channel on: channel id is found
        Returns None on: channel id is not found
    '''

    for channel in store['channels']:
        # If matching channel_id is found, return channel_id
        if channel['channel_id'] == channel_id:
            return channel

    # If no channel has the given channel_id, return None
    return None

def is_a_member(channel, temp_id):

    '''
    Function Description:
        Given a channel id and user id, checks if the user is in the channel.

    Arguments:
        channel_id (integer)        - channel id number
        temp_id (integer)           - temp id number

    Exceptions:
        N/A

    Return Value:
        Returns True on: user in channel is found
        Returns False on: user in channel is not found
    '''

    for member in channel['all_members']:
        # If a matching user is found, return True
        if member['u_id'] == temp_id:
            return True

    # If no user has the auth_user_id, return False
    return False

def is_channel_owner(channel, u_id):
    '''
    Function Description:
        Given a channel and a u_id, check if the user is an owner of the channel

    Arguments:
        channel (dictionary)  - data of the given channel
        u_id (int)            - user ID 

    Exceptions:
        N/A

    Return Value:
        Returns True on: user is found
        Returns False on: user is not found
    '''
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            return True
    return False


def add_user(u_id, channel_id, store):

    '''
    Function Description:
        Given a u_id, channel_id and storage, append user into channel members
        (for join and invite).

    Arguments:
        u_id (integer)              - user id number
        channel_id (integer)        - channel id number
        store (data)                - data storage

    Exceptions:
        N/A

    Return Value:
        N/A
    '''

    for user in store['users']:
        if user['u_id'] == u_id:
            person = user

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['all_members'].append(
            {
            'u_id': person['u_id'],
            'email': person['email'],
            'name_first': person['name_first'],
            'name_last': person['name_last'],
            'handle_str': person['handle_str'],
            'profile_img_url': person['profile_img_url']
            })
    
    

def channel_invite_v1(token, channel_id, u_id):

    '''
    Function Description:
        Invites a user with u_id to join a channel with channel_id, and the user
        is added to the channel. In both public and private channels, all
        members are able to invite users.

    Arguments:
        auth_user_id (integer)      - auth_user's id number
        channel_id (integer)        - channel id number
        u_id (integer)              - user's id number

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
                        - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is already a
                        member of the channel

        AccessError     - Occurs when auth_user_id is invalid
                        - Occurs when channel_id is valid and the authorised
                        user is not a member of the channel

    Return Value:
        Returns {} on: valid auth_user_id, channel_id and u_id
    '''
    
    store = data_store.get()
    # Find the user who had just registered
    found_user = search_user_token(token, store['users'])
    
    # If entered token does not belong to a user, raise accesserror
    if found_user is None:
        raise AccessError(description="Token entered is invalid")

    # Check if channel_id exists
    channel = search_channel_id(channel_id, store)

    # If the id does not exist
    if channel is None:
        raise InputError(description='Please enter a valid channel id')

    # Check if the authorised user is a member
    if is_a_member(channel, found_user['u_id']) is False:
        # If the channel id is valid but authorised user is not a member
        raise AccessError(description='Unauthorised member')

    # User already in channel
    if is_a_member(channel, u_id) is True:
        raise InputError(description="User already in channel")

    # Check that u_id is in users dict
    if is_a_valid_uid(u_id, store) is None:
        raise InputError("Please enter a valid user_id")

    # Appends user info into all_member dict
    add_user(u_id, channel_id, store)
    
    # Send a notification to the user who is being added
    notif_message = f"{found_user['handle_str']} added you to {channel['name']}"
    send_notification(channel_id, -1, notif_message, u_id)
    
    # Find the user whos being added to channel and update that users stat
    added_user = is_a_valid_uid(u_id, store)
    update_user_stat_channel(added_user, store)
    
    data_store.set(store)
    return {

    }

def channel_details_v1(token, channel_id):

    '''
    Function Description:
        Given a channel with ID channel_id that the authorised user is a member
        of, provide basic details about the channel.

    Arguments:
        auth_user_id (int)              - authorised user's id
        channel_id (int)                - channel's id

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
        AccessError     - Occurs when auth_user_id is invalid
                        - Occurs when channel_id is valid and the authorised
                        user is not a member of the channel

    Return Value:
        Returns {name, is_public, owner_members, all_members} on valid
        channel_id and authorised member
    '''

    store = data_store.get()

    # Check if token is valid
    found_user = search_user_token(token, store['users'])

    # If token is invalid
    if found_user is None:
        raise AccessError(description='INVALID TOKEN')

    # Check if channel_id exists
    channel = search_channel_id(channel_id, store)
    if channel is None:
        raise InputError(description='Please enter a valid channel id')

    # Check if the authorised user is a member
    if is_a_member(channel, found_user['u_id']) is False:
        # If the channel id is valid but authorised user is not a member
        raise AccessError(description='Unauthorised member')

    return {
        'name': channel['name'],
        'is_public': channel['is_public'],
        'owner_members': channel['owner_members'],
        'all_members': channel['all_members']
    }

def channel_messages_v1(token, channel_id, start):

    '''
    Function Description:
        Given a channel with channel_id that the authorised user is a member of,
        return up to 50 messages between index "start" and "start + 50".
        Otherwise, returns a new index "end" which is the value of "start + 50",
        or, if this function has returned the least recent messages in the
        channel, returns -1 in "end" to indicate there are no more messages to
        load after this return.

    Arguments:
        auth_user_id (int)          - auth_user's id number
        channel_id (int)            - channel id number
        start (int)                 - starting index

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
                        - Occurs when start is greater than the total number of
                        messages in the channel

        AccessError     - Occurs when auth_user_id is invalid
                        - Occurs when channel_id is valid and the authorised
                        user is not a member of the channel

    Return Value:
        Returns {messages, start, end} on: valid auth_user_id, channel_id and
        start index
    '''

    # Get data from datastore
    store = data_store.get()

    # Check if token is valid
    found_user = search_user_token(token, store['users'])
    
    # If token is invalid, raise accesserror
    if found_user is None:
        raise AccessError(description='TOKEN INVALID')

    # Find the channel given the channel id
    channel = search_channel_id(channel_id, store)

    # If channel was not found, raise inputerror
    if channel is None:
        raise InputError(description="Please enter a valid channel id")

    # Given channel id is valid, if the user is not a member of the channel,
    # raise accesserror
    if is_a_member(channel, found_user['u_id']) is False:
        raise AccessError(description="You are not a member of this channel")

    messages = channel['messages']
    total_messages = len(messages)

    # If start is greater than the total number of messages
    if start > total_messages:
        raise InputError(description="Start is greater than the total number of messages")

    # Create a list of messages to return
    messages_list = []

    # If there are less than 50 messages left to load
    if start + 50 >= total_messages:
        # Find number of messages left
        messages_left = total_messages - start

        # Append the remaining messages to message_list and update 
        # is_this_user_reacted accordingly
        for num in range(0, messages_left):
            messages_list.append(messages[num])
            change_is_this_user_reacted(messages_list, num, found_user)
        # Reverse messages list so its in the right order    
        messages_list.reverse()

        # Return the list of messages, start, and return end as -1 as there
        # were less than 50 messages left to load
        return {
            'messages': messages_list,
            'start': start,
            'end': -1
        }

    # If 50 messages can be loaded append the messages onto message_list
    index = 0
    for num in range(start, start + 50):
        messages_list.append(messages[total_messages - num - 1])
        change_is_this_user_reacted(messages_list, index, found_user)
        index += 1
    # Return the message_list, start and end
    
    data_store.set(store) 
    return {
        'messages': messages_list,
        'start': start,
        'end': start + 50
    }

# Helper function for join, checks if channel is public
def cant_access(channel_id, store):

    '''
    Function Description:
        Given a channel id and storage, checks if the channel is public.

    Arguments:
        channel_id (integer)        - channel id number
        store (data)                - data storage

    Exceptions:
        N/A

    Return Value:
        Returns True on: channel is public
        Returns False on: channel is not public
    '''

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            if channel['is_public'] is False:
                return True
    return False

def global_owner(auth_user_id, store):
    
    '''
    Function Description:
        Checks if auth_user_id is a global owner. If so, it can join any channel 
        regardless if it is public or private.

    Arguments:
        auth_user_id (integer)      - channel id number
        store (data)                - data storage

    Exceptions:
        N/A

    Return Value:
        Returns True on: id is global owner
        Returns False on: id is not global owner
    '''

    for user in store['users']:
        if user['u_id'] == auth_user_id:
            if user['permission_id'] == 1:
                return True
    return False

def channel_join_v1(token, channel_id):

    '''
    Function Description:
        Invites a user with u_id to join a channel with channel_id. Once
        invited, the user is added to the channel. In both public and private
        channels, all members are able to invite users.

    Arguments:
        auth_user_id (int)          - auth_user's id number
        channel_id (int)            - channel id number
        u_id (int)                  - users's id number

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
                        - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is already a
                        member of the channel

        AccessError     - Occurs when token is invalid
                        - Occurs when channel_id is valid and the authorised
                        user is not a member of the channel

    Return Value:
        Returns {} on: valid auth_user_id, channel_id and u_id
    '''

    store = data_store.get()
    
    # If entered token does not belong to a user, raise inputerror
    found_user = search_user_token(token, store['users'])
    if found_user is None:
        raise AccessError(description="Token entered is invalid")

    # Check for public or private channel
    if cant_access(channel_id, store) is True and \
       global_owner(found_user['u_id'], store) is False:
        raise AccessError(description="Channel not public")

    # Check if channel_id exists
    channel = search_channel_id(channel_id, store)
    if channel is None:
        raise InputError(description='Please enter a valid channel id')

    # User already in channel
    if is_a_member(channel, found_user['u_id']) is True:
        raise InputError(description="User already in channel")

    # Appends user to members list
    add_user(found_user['u_id'], channel_id, store)
    
    update_user_stat_channel(found_user, store)

    data_store.set(store)
    return {
    }

def channel_addowner_v1(token, channel_id, u_id):
    
    '''
    Function Description:
        Makes a user with the user id of u_id an owner of the channel

    Arguments:
        token (str)                 - authorisation hash
        channel_id (int)            - channel id number
        u_id (int)                  - users's id number

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
                        - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is not a
                        member of the channel
                        - Occurs when u_id refers to a user who is already a channel owner

        AccessError     - Occurs when Token is invalid
                        - Occurs when channel_id is valid but the user giving the
                          token is not an owner of the channel

    Return Value:
        Returns {}
    '''

    store = data_store.get()
    
    
    # Checking if the token is valid
    token_user = search_user_token(token, store['users'])
    if token_user is None:
        raise AccessError(description="Invalid Token")
    
    # Get the u_id of the token user
    token_uid = token_user['u_id']

    # Checking if the channel_id is valid
    channel = search_channel_id(channel_id, store)
    if channel is None:
        raise InputError(description="Invalid Channel_id")

    # Check if token_uid is a member of the channel
    if is_a_member(channel, token_uid) is False:
        raise AccessError(description="Authorised user is not a member of the channel")

    # Check if the token_uid is a channel owner
    if is_channel_owner(channel, token_uid) is False:
        if token_user['permission_id'] != 1:
            raise AccessError(description="You do not have owner permissions")

    # Check if u_id is valid
    if is_a_valid_uid(u_id, store) is None:
        raise InputError("Invalid u_id")

    # Check if u_id is a member of the channel
    if is_a_member(channel, u_id) is False:
        raise InputError(description="User is not a member of the channel")

    # Check if u_id is already a member of the channel
    if is_channel_owner(channel, u_id,) is True:
        raise InputError(description="Already a channel owner")

    for person in store['users']:
        if person['u_id'] == u_id:
            # Storing data in user
            user = {'u_id': u_id,
                    'email': person['email'], 
                    'name_first': person['name_first'], 
                    'name_last': person['name_last'], 
                    'handle_str': person['handle_str'],
                    'profile_img_url': person['profile_img_url']
                    }
                    
    channel['owner_members'].append(user)

    data_store.set(store)

    return {    
    }

def channel_removeowner_v1(token, channel_id, u_id):
    
    '''
    Function Description:
        Removes a user with the user id of u_id as an owner of the channel

    Arguments:
        token (str)                 - authorisation hash
        channel_id (int)            - channel id number
        u_id (int)                  - users's id number

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel
                        - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is not an
                        owner of the channel
                        - Occurs when u_id refers to a user who is the only channel owner

        AccessError     - Occurs when Token is invalid
                        - Occurs when channel_id is valid but the user giving the
                          token is not an owner of the channel

    Return Value:
        Returns {}
    '''

    store = data_store.get()

    # Check if token is valid
    token_user = search_user_token(token, store['users'])
    if token_user is None:
        raise AccessError(description="Invalid Token")
    
    # Get token u_id
    token_uid = token_user['u_id']

    # Check if the channel_id is valid
    channel = search_channel_id(channel_id, store) 
    if channel is None:
        raise InputError(description="Invalid Channel_id")

    # Check if token_uid is a member of the channel
    if is_a_member(channel, token_uid) is False:
        raise AccessError(description="Authorised user is not a member of the channel")

    # Check if the token_uid is a channel owner
    if is_channel_owner(channel, token_uid) is False:
        if token_user['permission_id'] != 1:
            raise AccessError(description="You do not have owner permissions")

    # Check if u_id is valid
    if is_a_valid_uid(u_id, store) is None:
        raise InputError("Invalid u_id")

    # Check if u_id2 is an owner of the channel
    if is_channel_owner(channel, u_id) is False:
        raise InputError(description="Not a member of channel")

    # Check if u_id is the only channel owner
    for user in channel['owner_members']:
        if user['u_id'] == u_id and len(channel['owner_members']) == 1:
            raise InputError(description="Cannot remove user as they are the only owner of the channel")

    # Remove the user as an owner
    for owner in channel['owner_members']:
        if owner['u_id'] == u_id:
            channel['owner_members'].remove(owner)
    
    data_store.set(store)
    return {
    }

# Function for the implementation of channel/leave
def channel_leave_v1(token, channel_id):
    
    '''
    Function Description:
        Removes a user from a channel members list

    Arguments:
        token (str)                 - authorisation hash
        channel_id (int)            - channel id number

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid
                        channel

        AccessError     - Occurs when Token is invalid
                        - Occurs when channel_id is valid but the user is
                        not a member of the channel

    Return Value:
        Returns {}
    '''

    store = data_store.get()

    # Check if token is valid
    token_user = search_user_token(token, store['users'])
    if token_user is None:
        raise AccessError(description="Invalid Token")
    
    # Get the token user's u_id
    token_uid = token_user['u_id']

    # Checking if the channel_id is valid
    channel = search_channel_id(channel_id, store)
    if channel is None:
        raise InputError(description="Invalid Channel_id")

    # Check if token_uid is a member of the channel
    if is_a_member(channel, token_uid) is False:
        raise AccessError(description="Not a member of channel")

    # Removing user from owner_members and members lists
    for owner in channel['owner_members']:
        if owner['u_id'] == token_uid:
            channel['owner_members'].remove(owner)

    for member in channel['all_members']:
        if member['u_id'] == token_uid:
            channel['all_members'].remove(member)
    
    update_user_stat_channel(token_user, store)
    
    data_store.set(store)

    return {
    }
