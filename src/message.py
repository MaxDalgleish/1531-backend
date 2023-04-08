'''
message.py implementation

    Description:
        Implementations of message functions

    Functions:
        - Main functions:
            - message_send(token, channel_id, message)
            - message_senddm(token, dm_id, message)
            - message_sendlater(token, channel_id, message, time_sent)
            - message_sendlaterdm(token, dm_id, message, time_sent)
            - message_remove(token, message_id)
            - message_edit(token, message_id, message)
            - message_react(token, message_id, react_id)
            - message_pin(token, message_id)
            - message_unpin(token, message_id)
            - message_share(token, og_message_id, message, channel_id, dm_id)
        - Helper functions:
            - get_new_message_id(store)
            - tag_users_channel_msg(message, sender, channel, store)
            - tag_users_dm_msg(message, sender, dm, store)
            - get_tagged_users(message)
            - is_tagged_user_valid_channel(handle, channel)
            - is_tagged_user_valid_dm(handle, dm)
            - get_user_given_handle(handle, store)
            - get_message(message_id, all_messages)
            - can_edit_dm_message(sender, user, dm)
            - is_a_channel_owner(u_id, channel)
            - can_edit_channel_message(sender, user, channel)
            - delete_dm_message(message, store, dm_id)          
            - delete_channel_message(message_id, store, channel)
            - edit_dm_message(message_id, store, dm)
            - edit_channel_message(message_id, store, channel)
            - already_reacted(message_reacts, react_id, u_id)
            - react_to_message(stored_message_dict, react_id, u_id)
'''

from .channel import is_channel_owner
from .data_store import data_store
from .error import InputError, AccessError
from .helpers import *
import datetime, time, threading, re

# Send a notification to users tagged in a channel message
def tag_users_channel_msg(message, sender, channel, store):
    
    # Check for any tagged users
    tagged_users = get_tagged_users(message)

    # Cut the message down to the first 20 chars or less
    if len(message) < 20:
        shortened_message = message[0:len(message)]
    else:
        shortened_message = message[0:20]

    notif_msg = f"{sender['handle_str']} tagged you in {channel['name']}: {shortened_message}"

    # Check that the user is a valid member of the channel, if they are, send
    # them a notification that they were tagged
    for handle in tagged_users:
        if is_tagged_user_valid_channel(handle, channel):
            tagged_user = get_user_given_handle(handle, store)
            send_notification(channel['channel_id'], -1, notif_msg, tagged_user['u_id'])

# Send notifications to users tagged in a dm message
def tag_users_dm_msg(message, sender, dm, store):

    # Check for any tagged users
    tagged_users = get_tagged_users(message)

    # Cut the message down to the first 20 chars
    if len(message) < 20:
        shortened_message = message[0:len(message)]
    else:
        shortened_message = message[0:20]

    notif_msg = f"{sender['handle_str']} tagged you in {dm['name']}: {shortened_message}"

    # Check that the user is a valid member of the dm, if they are, send them a
    # notification that they were tagged
    for handle in tagged_users:
        if is_tagged_user_valid_dm(handle, dm):
            tagged_user = get_user_given_handle(handle, store)
            send_notification(-1, dm['dm_id'], notif_msg, tagged_user['u_id'])

# Gets a list of users tagged in a message
def get_tagged_users(message):

    tagged_handles = []

    # Split message by "@" symbols
    first_list = re.split('[@]', message)

    new_list = []

    # Split list by non-alphanumeric characters
    for element in first_list:
        new_list.append(re.split('[^a-zA-Z0-9]', element)[0])

    # Append tagged handles to handles list and get rid of repeated tags
    for handle in new_list:
        if handle != "" and handle not in tagged_handles:
            tagged_handles.append(handle)

    return tagged_handles

# Checks if a tagged user is a valid member of a channel
def is_tagged_user_valid_channel(handle, channel):

    for user in channel['all_members']:
        if user['handle_str'] == handle:
            return True
    return False

# Checks if a tagged user is a valid member of a dm
def is_tagged_user_valid_dm(handle, dm):

    for user in dm['members']:
        if user['handle_str'] == handle:
            return True
    return False

# Given a user's handle, returns their user dict
def get_user_given_handle(handle, store):
    for user in store['users']:
        if user['handle_str'] == handle:
            return user

# Returns a new unique message_id
def get_new_message_id(store):
    
    # Get unique message_id
    new_message_id = store['message_ids']

    # Increase message_id counter for the next message
    store['message_ids'] += 1
    
    return new_message_id

def message_send(token, channel_id, message):
    
    '''
    Given a valid token, channel_id, and message, message_send will send the
    message from the authorised user into the channel given by channel_id

    Arguments:
        token (str)             - authorised user's hash
        channel_id (int)        - a specific channel's id
        message (str)           - the message the user wants to send

    Exceptions:
        InputError              - Occurs when channel_id does not refer to a 
                                  valid channel
                                - length of message is less than 1 or over 1000
                                  characters
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when channel_id is valid and the 
                                  authorised user is not a member of the channel

    Return Value:
        Returns {message_id} on valid token, channel_id and message
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
    
    msg_len = len(message)
    # Check if length of message is < 1 character or > 1000 characters
    if msg_len < 1 or msg_len > 1000:
        raise InputError(description='Message length must be between 1 and 1000 characters')

    # Get new message_id
    message_id = get_new_message_id(store)

    # Check if any users were tagged and send them a notification if they are
    # valid members
    tag_users_channel_msg(message, user, channel, store)

    # Get the current time
    t = datetime.datetime.now()

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}

    # Create a message dictionary where time created is a unix timestamp
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': int(time.mktime(t.timetuple())),
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'channel_id': channel['channel_id']}

    # Append message dictionary to channel messages and also all messages
    store['messages'].append(message_dict)
    channel['messages'].append(message_dict)
    
    # Update user and workspace message given user
    update_user_stat_message(user, store)
    update_workspace_message(user, store)
    
    data_store.set(store)
    
    return {
        'message_id': message_id
    }

def message_senddm(token, dm_id, message):

    '''
    Given a valid token, dm_id, and message, message_send will send the
    message from the authorised user into the dm given by dml_id

    Arguments:
        token (str)             - authorised user's hash
        dm_id (int)             - a specific dm's id
        message (str)           - the message the user wants to send

    Exceptions:
        InputError              - Occurs when dm_id does not refer to a valid dm
                                - length of message is less than 1 or over 1000
                                  characters
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when dm_id is valid and the authorised
                                  user is not a member of the dm

    Return Value:
        Returns {message_id} on valid token, dm_id and message
    '''
    
    store = data_store.get()

    # Check if token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if dm_id refers to a valid dm
    dm = find_dm(dm_id, store['dms'])
    if dm is None:
        raise InputError(description='Invalid dm_id')

    # Check if user is a member of the dm
    if is_a_member_dm(user['u_id'], dm['members']) is False:
        raise AccessError(description='You are not a member of this dm')

    message_length = len(message)

    # Check if message is empty or > 1000 characters
    if message_length < 1 or message_length > 1000:
        raise InputError(description='Message length must be between 1 and 1000 characters')

    # Get message_id
    message_id = get_new_message_id(store)

    # Check if any users were tagged and send them a notification if they are
    # valid members
    tag_users_dm_msg(message, user, dm, store)

    # Get the current time
    t = datetime.datetime.now()

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}

    # Create a message_dict where time created is a unix timestamp
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': int(time.mktime(t.timetuple())),
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'dm_id': dm['dm_id']}

    # Append message dictionary to channel messages and also all messages
    store['messages'].append(message_dict)
    dm['messages'].append(message_dict)
    
    # Update stat and workspace message given user
    update_user_stat_message(user, store)
    update_workspace_message(user, store)
    
    data_store.set(store)

    return {
        'message_id': message_id
    }

# Checks if a message_id is exists, if it does, return message_dict, if it 
# doesn't return None
def get_message(message_id, all_messages):
    
    for message in all_messages:
        if message['message_id'] == message_id and message['time_created'] != 0:
            return message
    return None

# Checks whether a given user has permission to edit a dm message
def can_edit_dm_message(sender, user, dm):
    
    # If they were the sender or the dm creator, they can edit the dm message
    if sender == user or dm['creator']['u_id'] == user:
        return True

    # Else the user does not have permission to edit the dm message
    else:
        return False

# Checks if a user is an owner of a given channel
def is_a_channel_owner(u_id, channel):
    for user in channel['owner_members']:
        if user['u_id'] == u_id:
            return True
    return False

# Checks whether a given user has permission to edit a channel message
def can_edit_channel_message(sender, user, channel):
    
    # If the user was the sender, they can edit the channel message
    if sender == user['u_id']:
        return True

    # If the user is a channel owner, they can edit the channel message
    elif is_a_channel_owner(user['u_id'], channel):
        return True

    # If the user is a member and is a global owner, they can edit the 
    # channel message
    elif user['permission_id'] == 1:
        return True
    
    # Else the user does not have permission to edit the channel message
    else:
        return False

# Changes message in message_store and deletes message from dm['messages']
def delete_dm_message(message_id, store, dm):
    
    # Change time_created of message in store['messages'] to 0 and remove other keys
    index = 0
    for message_dict in store['messages']:
        if message_dict['message_id'] == message_id:
            store['messages'][index]['time_created'] = 0
        index += 1

    # Find the message in dm['messages'] and delete it
    for dm_message in dm['messages']:
        if dm_message['time_created'] == 0:
            dm['messages'].remove(dm_message)

# Changes message in store['messages'] and deletes message from channel['messages']
def delete_channel_message(message_id, store, channel):
    
    # Changes time_created in store['messages'] to 0 and remove other keys
    index = 0
    for message_dict in store['messages']:
        if message_dict['message_id'] == message_id:
            store['messages'][index]['time_created'] = 0
        index += 1

    # Deletes message from channel['messages']
    for message in channel['messages']:
        if message['time_created'] == 0:
            channel['messages'].remove(message)
    
# Removes a message from the channel or dm it was sent in
def message_remove(token, message_id):

    '''
    Given a valid token and message_id removes the message given by message_id
    from the channel or dm it was sent in.

    Arguments:
        token (str)             - authorised user's hash
        message_id (int)        - the given message's id

    Exceptions:
        InputError              - Occurs when message_id does not refer to a 
                                  valid message
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when the token user is a member of the
                                  channel or dm the message was sent in but they 
                                  did not send the message and do not have owner
                                  permissions in the channel or dm

    Return Value:
        Returns {} on valid token and message_id
    '''

    store = data_store.get()
    
    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if message_id exists, if message_id is 0, it is a removed message and
    # is invalid
    message = get_message(message_id, store['messages'])
    if message is None:
        raise InputError(description='This message_id does not exist')

    # If message was sent in a dm
    if 'dm_id' in message:

        # Get dm dictionary
        dm = find_dm(message['dm_id'], store['dms'])

        # Check that the user is a member
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')

        # If they were the user who sent the message or the dm creator
        if can_edit_dm_message(message['u_id'], user['u_id'], dm):
            delete_dm_message(message_id, store, dm)

        # If they did not send the message and are not the creator of the dm
        else:
            raise AccessError(
                description='You do not have permission to remove this dm message')

    # If message was sent in a channel
    else:
        
        # Get channel dictionary
        channel = get_channel(message['channel_id'], store)

        # Check that the user is a member
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')
        
        # If the user has permissions (they sent the message, they are a channel
        # owner or they are member who is a global owner)
        if can_edit_channel_message(message['u_id'], user, channel):
            delete_channel_message(message_id, store, channel)

        # If the user is a member but did not send the message, is not a channel
        # owner and is not a global owner
        else:
            raise AccessError(description='You do not have permission to remove this channel message')
    
    # Update workspace and stat message given user
    update_user_stat_message(user, store)
    update_workspace_message(user, store)
    
    data_store.set(store)

    return {    

    }

# Helpers for message_edit
def edit_dm_message(message_id, message, store, dm):
    
    # Edit the message in store['messages']
    for message_dict in store['messages']:
        if message_dict['message_id'] == message_id:
            message_dict['message'] = message

    # Edit the message in dm['messages']
    for dm_message in dm['messages']:
        if dm_message['message_id'] == message_id:
            dm_message['message'] = message

    sender = is_a_valid_uid(message_dict['u_id'], store)

    # Check if any users were tagged and send them a notification if they are
    # valid members
    tag_users_dm_msg(message, sender, dm, store)

def edit_channel_message(message_id, message, store, channel):
    
    # Edit the message in store['messages']
    for message_dict in store['messages']:
        if message_dict['message_id'] == message_id:
            message_dict['message'] = message

    # Edit the message in channel['messages']
    for channel_message in channel['messages']:
        if channel_message['message_id'] == message_id:
            channel_message['message'] == message

    # Get sender's dict
    sender = is_a_valid_uid(message_dict['u_id'], store)

    # Check if any users were tagged and send them a notification if they are
    # valid members
    tag_users_channel_msg(message, sender, channel, store)

def message_edit(token, message_id, message):
    
    '''
    Given a valid token, message_id and message, message_edit edits the message
    that the message_id refers to in the channel or dm it was sent in to the new
    inputted message. If the message inputted is an empty str, the message will
    be deleted

    Arguments:
        token (str)             - authorised user's hash
        message_id (int)        - the given message's id
        message(str)            - the new message

    Exceptions:
        InputError              - Occurs when message_id does not refer to a 
                                  valid message within a channel/DM that the
                                  authorised user has joined
                                - Occurs when length of message is over 1000 
                                  characters
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when the auth user is a member of the
                                  channel or dm the message was sent in but they 
                                  did not send the message and do not have owner
                                  permissions in the channel or dm

    Return Value:
        Returns {} on valid token and message_id
    '''

    store = data_store.get()

    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if message_id exists, if it is 0, it is a removed message and is 
    # invalid
    message_dict = get_message(message_id, store['messages'])
    if message_dict is None:
        raise InputError(description='This message_id does not exist')

    # If message was sent in a dm
    if 'dm_id' in message_dict:

        # Get dm dictionary
        dm = find_dm(message_dict['dm_id'], store['dms'])

        # Check that the user is a member of the dm
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')

        # If they have edit permissions (if they were the sender or they are 
        # the dm creator)
        if can_edit_dm_message(message_dict['u_id'], user['u_id'], dm):
            
            # Raise an InputError if message length is over 1000 characters
            if len(message) > 1000:
                raise InputError(description='A message cannot be over 1000 characters in length')
            
            # If the message length is 0 (ie empty string) remove the message
            elif len(message) == 0:
                delete_dm_message(message_id, store, dm)
            
            else:
                edit_dm_message(message_id, message, store, dm)
        
        # If they did not send the message and are not the creator of the dm
        else:
            raise AccessError(description='You do not have permission to edit this dm message')
    
    # If message was sent in a channel
    else:
        
        # Get channel dictionary
        channel = get_channel(message_dict['channel_id'], store)

        # Check that the user is a member of the channel
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')
        
        # If the user has edit permissions (they were the message sender, they
        # are a channel owner, or they are a global owner)
        if can_edit_channel_message(message_dict['u_id'], user, channel):
            
            # Raise an InputError if message length is over 1000 characters
            if len(message) > 1000:
                raise InputError(description='A message cannot be over 1000 characters in length')
            
            # If the message length is 0 (ie empty string) remove the message
            elif len(message) == 0:
                delete_channel_message(message_id, store, channel)
            
            else:
                edit_channel_message(message_id, message, store, channel)
        
        # If the user is a member but did not send the message, is not a channel
        # owner and is not a global owner
        else:
            raise AccessError(description='You do not have permission to edit this channel message')
    
    data_store.set(store)

    return {

    }

# Checks if a given user has already reacted to a message with a certain react 
# id
def already_reacted(message_reacts, react_id, u_id):

    if u_id in message_reacts[0]['u_ids']:
        return True
    return False


# React to a message
def react_to_message(stored_message_dict, u_id, handle, name):

    # Append u_id to u_ids list in react dict
    stored_message_dict['reacts'][0]['u_ids'].append(u_id)

    # Change is_this_user_reacted to True
    stored_message_dict['reacts'][0]['is_this_user_reacted'] = True

    # Send a notification to message sender 
    notif_message = f"{handle} reacted to your message in {name}"
    
    # If the message was a dm message
    if 'dm_id' in stored_message_dict:

        dm_id = stored_message_dict['dm_id']
        send_notification(-1, dm_id, notif_message, stored_message_dict['u_id'])

    # If the message was a channel message
    else: 
        
        channel_id = stored_message_dict['channel_id']
        send_notification(channel_id, -1, notif_message, stored_message_dict['u_id'])

# Given a valid message id in a channel or dm the auth_user is a member of,
# reacts to the message
def message_react(token, message_id, react_id):

    '''    
    Given a message within a channel or DM the authorised user is part of, 
    add a "react" to that particular message.

    Arguments:
        token (str)             - authorised user's hash
        message_id (int)        - the given message's id
        react_id(int)           - id of the given react

    Exceptions:
        InputError              - message_id is not a valid message within a 
                                  channel or DM that the authorised user has 
                                  joined
                                - react_id is not a valid react ID - currently, 
                                  the only valid react ID the frontend has is 1
                                - the message already contains a react with ID 
                                  react_id from the authorised user
        
        AccessError             - Occurs when token passed is invalid

    Return Value:
        Returns {} on valid token, message_id, and react_id
    '''

    store = data_store.get()

    # Gets user dict if token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='Token is invalid')

    # Gets stored message dict if message_id is valid
    message = get_message(message_id, store['messages'])
    if message is None:
        raise InputError(description='This message_id does not exist')

    # If the react id is invalid:
    if react_id != 1:
        raise InputError(description='This react id is invalid')

    # Check if auth user has already reacted to this message with the same react
    if already_reacted(message['reacts'], react_id, user['u_id']):
        raise InputError(description='You have already reacted to this message with this react')

    # If message was sent in a dm
    if 'dm_id' in message:

        dm = find_dm(message['dm_id'], store['dms'])

        # Check if the auth_user is a member of the dm
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')
        
        name = dm['name'] 

    # Else the message is a channel message
    else:
        # Get channel dictionary
        channel = get_channel(message['channel_id'], store)

        # Check that the user is a member of the channel
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')

        name = channel['name']

    react_to_message(message, user['u_id'], user['handle_str'], name)

    data_store.set(store)

    return {

    }

# Allows a user to unreact to a dm message they have reacted to
def unreact_to_dm_message(stored_message, u_id):
    
    # Removes authorised user's id from react u_ids list
    for user_id in stored_message['reacts'][0]['u_ids']:
        if user_id == u_id:
            stored_message['reacts'][0]['u_ids'].remove(user_id)

    # If the authorised user was the sender
    if stored_message['u_id'] == u_id:
        stored_message['reacts'][0]['is_this_user_reacted'] = False

# Allows a user to unreact to a channel message they have reacted to
def unreact_to_channel_message(stored_message, u_id):
    
    # Removes authorised user's id from react u_ids list
    for user_id in stored_message['reacts'][0]['u_ids']:
        if user_id == u_id:
            stored_message['reacts'][0]['u_ids'].remove(user_id)

    # If the authorised user was the sender
    if stored_message['u_id'] == u_id:
        stored_message['reacts'][0]['is_this_user_reacted'] = False

def message_unreact(token, message_id, react_id):
    '''    
    Given a message within a channel or DM the authorised user is part of, 
    remove a "react" to that particular message.
    
    Arguments:
        token (str)             - authorised user's hash
        message_id (int)        - the given message's id
        react_id(int)           - id of the given react

    Exceptions:
        InputError              - message_id is not a valid message within a 
                                  channel or DM that the authorised user has 
                                  joined
                                - react_id is not a valid react ID - currently, 
                                  the only valid react ID the frontend has is 1
                                - the message does not contain a react with ID 
                                  react_id from the authorised user
        
        AccessError             - Occurs when token passed is invalid

    Return Value:
        Returns {} on valid token, message_id, react_id, and message contains a 
        react from the authorised user
    '''
    
    store = data_store.get()

    # Gets user dict if token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='Token is invalid')

    # Gets stored message dict if message_id is valid
    message = get_message(message_id, store['messages'])
    if message is None:
        raise InputError(description='This message_id does not exist')

    # If the react id is invalid:
    if react_id != 1:
        raise InputError(description='This react id is invalid')

    # If the user has not reacted to the message with the react yet
    if not already_reacted(message['reacts'], react_id, user['u_id']):
        raise InputError(description='You have not reacted to this message with this react')
    
    # If the message is a dm message
    if 'dm_id' in message:

        dm = find_dm(message['dm_id'], store['dms'])

        # Check if the auth_user is a member of the dm
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')

        unreact_to_dm_message(message, user['u_id'])

    # Else the message is a channel message
    else:
        # Get channel dictionary
        channel = get_channel(message['channel_id'], store)

        # Check that the user is a member of the channel
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')
        
        # React to channel message
        unreact_to_channel_message(message, user['u_id'])

    return {

    }
    
def message_pin(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned"

    Arguments:
        token (str)             - authorised user's hash
        message_id (int)        - the given message's id

    Exceptions:
        InputError              - Occurs when message_id does not refer to a 
                                  valid message within a channel/DM that the
                                  authorised user has joined
                                - The message is already pinned
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when the message_id refers to a valid message in
                                  the channel or dm but the user doesn't have owner permissions

    Return Value:
        Returns {} on valid token and message_id
    '''

    store = data_store.get()

    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if message_id exists, if it is 0, it is a removed message and is 
    # invalid
    message_dict = get_message(message_id, store['messages'])
    if message_dict is None:
        raise InputError(description='This message does not exist')

    # If message was sent in a dm
    if 'dm_id' in message_dict:

        # Get dm dictionary
        dm = find_dm(message_dict['dm_id'], store['dms'])

        # Check if the user is a member of the dm the message came from
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')

        # Check if the user is the creator of the dm
        if dm['creator']['u_id'] != user['u_id']:
            raise AccessError(description='You do not have owner permissions')
    
    # If message was sent in a channel
    else:

        # Get channel dictionary
        channel = get_channel(message_dict['channel_id'], store)

        # Check that the user is a member of the channel the message came from
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')
        
        # Check if the user is a global owner or channel owner
        if is_channel_owner(channel, user['u_id']) is False:
            if user['permission_id'] != 1:
                raise AccessError(description='You do not have owner permissions')


    # Check if the message is already pinned
    if message_dict['is_pinned'] is True:
        raise InputError(description='Message is already pinned')

    # Change the is_pinned status to be True
    message_dict['is_pinned'] = True

    # Saving the change in data
    data_store.set(store)

    return {

    }

def message_unpin(token, message_id):
    '''
    Given a message within a channel or DM, remove its mark as "pinned"

    Exceptions:
        InputError              - Occurs when message_id does not refer to a 
                                  valid message within a channel/DM that the
                                  authorised user has joined
                                - The message is already unpinned
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when the message_id refers to a valid message in
                                  the channel or dm but the user doesn't have owner permissions

    Return Value:
        Returns {} on valid token and message_id
    '''

    store = data_store.get()

    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if message_id exists, if it is 0, it is a removed message and is 
    # invalid
    message_dict = get_message(message_id, store['messages'])
    if message_dict is None:
        raise InputError(description='This message_id does not exist')

    # If message was sent in a dm
    if 'dm_id' in message_dict:

        # Get dm dictionary
        dm = find_dm(message_dict['dm_id'], store['dms'])

        # Check if the user is a member of the dm the message came from
        if is_a_member_dm(user['u_id'], dm['members']) is False:
            raise InputError(description='You are not a member in the dm that this message was sent in')

        # Check if the user is the creator of the dm
        if dm['creator']['u_id'] != user['u_id']:
            raise AccessError(description='You do not have owner permissions')
    
    # If message was sent in a channel
    else:

        # Get channel dictionary
        channel = get_channel(message_dict['channel_id'], store)

        # Check that the user is a member of the channel the message came from
        if is_a_member(user['u_id'], channel) is False:
            raise InputError(description='You are not a member in the channel that this message was sent in')
        
        # Check if the users are either a global owner or a channel creator
        if is_channel_owner(channel, user['u_id']) is False:
            if user['permission_id'] != 1:
                raise AccessError(description='You do not have owner permissions')

    # Check if the message is already unpinned
    if message_dict['is_pinned'] is False:
        raise InputError(description='Message is already unpinned')

    # Change the is_pinned status to be False
    message_dict['is_pinned'] = False

    # Saving the change in data
    data_store.set(store)

    return {

    }

# Sends a message to a channel for use in message/share
def message_share_send_channel(user, channel, message, store):

    # Get message_id
    message_id = get_new_message_id(store)

    # Check for any tagged users
    tag_users_channel_msg(message, user, channel, store)

    # Get the current time
    t = datetime.datetime.now()

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}

    # Create a message dictionary where time created is a unix timestamp
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': int(time.mktime(t.timetuple())),
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'channel_id': channel['channel_id']}

    # Append message dictionary to channel messages and also all messages
    store['messages'].append(message_dict)
    channel['messages'].append(message_dict)
    
    data_store.set(store)
    
    return {
        'message_id': message_id
    }

# Sends a message to a dm for use in message/share
def message_share_send_dm (user, dm, message, store):

    # Get message_id
    message_id = get_new_message_id(store)

    # Check for any tagged users
    tag_users_dm_msg(message, user, dm, store)

    # Get the current time
    t = datetime.datetime.now()

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}

    # Create a message_dict where time created is a unix timestamp
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': int(time.mktime(t.timetuple())),
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'dm_id': dm['dm_id']}

    # Append message dictionary to channel messages and also all messages
    store['messages'].append(message_dict)
    dm['messages'].append(message_dict)
    
    data_store.set(store)

    return {
        'message_id': message_id
    }

def message_share(token, og_message_id, message, channel_id, dm_id):
    '''
    Share a message to another channel

    Arguments:
        token (str)             - authorised user's hash
        og_message_id (int)     - the original message id
        message (string)        - the message being shared
        channel_id (int)        - the id of the channel being shared to
        dm_id (int)             - the id of the dm being shared to

    Exceptions:
        InputError              - Occurs when both channel_id and dm_id are invalid
                                - Neither channel_id nor dm_id are invalid
                                - Occurs when og_message_id does not refer to a valid message
                                  within a channel/dm that the user has joined
                                - Occurs when the length of the message is more than 1000 characters
                                - The message is already unpinned
        
        AccessError             - Occurs when token passed is invalid
                                - Occurs when channel_id and dm_id are valid but the authorised
                                  user has not joined the channel or dm they are trying to share to

    Return Value:
        Returns {shared_message_id} on valid token and og_message_id
    '''

    store = data_store.get()

    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Gets stored message dict if message_id is valid
    og_message = (get_message(og_message_id, store['messages']))

    # Checking if both the channel and dm are invalid
    if is_dm_valid(dm_id,store) is False and is_channel_valid(channel_id, store) is False:
        raise InputError(description='No specified channel or dm given')

    # Checking if both the channel and the dm are valid
    if is_dm_valid(dm_id, store) is True and is_channel_valid(channel_id, store) is True:
        raise InputError(description='No specified channel or dm given')

    # For sharing to a channel
    if dm_id == -1:
        
        # Getting the target channel for the message
        target_channel = get_channel(channel_id, store)

        # Check if the user is a member of the target channel
        if is_a_member(user['u_id'], target_channel) is False:
            raise AccessError(description='Not a member of the given channel')
        
        # Checks if the given message_id corresponds to a message
        if og_message is None or og_message_id == 0:
            raise InputError(description='This message_id does not exist')

        # Checking if the og_message came from a dm
        if 'dm_id' in og_message:
            og_dm = find_dm(og_message['dm_id'], store['dms'])

            # Check if the user is a member of the dm the message came from
            if is_a_member_dm(user['u_id'], og_dm['members']) is False:
                raise InputError(description='You are not a member in the dm that this message was sent in')

        # Else the message came from a channel
        else:
            og_channel = get_channel(og_message['channel_id'], store)

            # Check that the user is a member of the channel the message came from
            if is_a_member(user['u_id'], og_channel) is False:
                raise InputError(description='You are not a member in the channel that this message was sent in')

        # Checking if the message length is greater than 1000 characters
        if len(message) > 1000:
            raise InputError(description='Message length is greater than 1000')
 
        # Creating the new message
        new_message = (f"''''''\n{og_message['message']}\n''''''")
        if message != '':
            new_message = (f"{message}\n\n''''''\n{og_message['message']}\n''''''")

        # Sending the new message in the channel and getting the new message id
        shared_message_id = message_share_send_channel(user, target_channel, new_message, store)
        
        # Update workspace and stat message given user
        update_user_stat_message(user, store)
        update_workspace_message(user, store)

    # For sharing to a dm
    if channel_id == -1:
        
        target_dm = find_dm(dm_id, store['dms'])
        
        # Checks if the user is a member of the target dm
        if is_a_member_dm(user['u_id'], target_dm['members']) is False:
            raise AccessError(description='Not a member of the given dm')
        
        # Checks if the given message_id corresponds to a message
        if og_message is None or og_message_id == 0:
            raise InputError(description='This message_id does not exist')

        # Checking if the og_message came from a dm
        if 'dm_id' in og_message:
            og_dm = find_dm(og_message['dm_id'], store['dms'])

            # Check if the user is a member of the dm the message came from
            if is_a_member_dm(user['u_id'], og_dm['members']) is False:
                raise InputError(description='You are not a member in the dm that this message was sent in')

        # Checking if the og_message came from a channel
        elif 'channel_id' in og_message:
            og_channel = get_channel(og_message['channel_id'], store)

            # Check that the user is a member of the channel the message came from
            if is_a_member(user['u_id'], og_channel) is False:
                raise InputError(description='You are not a member in the channel that this message was sent in')

        # Checking if the message length is greater than 1000 characters
        if len(message) > 1000:
            raise InputError(description='Message length is greater than 1000')

        # Creating the new message
        new_message = (f"''''''\n{og_message['message']}\n''''''")
        if message != '':
            new_message = (f"{message}\n\n''''''\n{og_message['message']}\n''''''")

        # Sending the new message in the dm and getting the new message_id
        shared_message_id = message_share_send_dm(user, target_dm, new_message, store)
        
        # Update workspace and stat message given user
        update_user_stat_message(user, store)
        update_workspace_message(user, store)

    # Returning the new message_id 
    return {'shared_message_id': shared_message_id['message_id']}    

def message_sendlater(token, channel_id, message, time_sent):
    """
    Function sends a message in the future specified by the user in the 
    channel specified by the user.

    Arguments:
        token (<string type>)    - token of the valid user
        channel_id (<int type>)    - id num of the channel to send the message
        message (<string type>)    - message to be sent
        time_sent (<int (unix timestamp) type>)    - time to send the message
        ...

    Exceptions:
        InputError  - Occurs when:
            - channel_id doesn't refer to a valid channel
            - the message is over 1000 characters
            - time_sent refers to a time in the past
            - 
        AccessError - Occurs when:
            - channel_id is valid but user is not a member of the channel
            - token is invalid

    Return Value:
        Returns {"message_id": message_id} if there is no errors and the message
        is bring threaded and sent later.
    """
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

    # Check if length of message is < 1 character or > 1000 characters
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Message length must be between 1 and 1000 characters')

    # Get message_id
    message_id = get_new_message_id(store)

    # Get the current time
    rn = datetime.datetime.now()

    unix_rn = int(time.mktime(rn.timetuple()))

    # Check that the user didn't give us a time in the past
    if unix_rn > time_sent:
        raise InputError(description="You cannot send a message to the past, even though that would be pretty cool")
    
    # Get the unix time difference
    time_delta = time_sent - unix_rn

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}
    
    # Create message dictionary
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': unix_rn,
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'channel_id': channel['channel_id']}

    # Threading for the appending the message into messages and dms
    # Addtional threading for saving to data
    messages_thread = threading.Timer(time_delta, add_to_list, args=(store['messages'], message_dict))
    channel_thread = threading.Timer(time_delta, add_to_list, args=(channel["messages"], message_dict))
    tagging_thread = threading.Timer(time_delta, tag_users_channel_msg, args=(message, user, channel, store))
    stats_user_thread = threading.Timer(time_delta, update_user_stat_message, args=(user, store))
    stats_workspace_thread = threading.Timer(time_delta, update_workspace_message, args=(user, store))
    
    # Start the threads
    messages_thread.start()
    channel_thread.start()
    tagging_thread.start()
    stats_user_thread.start()
    stats_workspace_thread.start()
    
    return {
        'message_id': message_id
    }

def message_sendlaterdm(token, dm_id, message, time_sent):
    """
    Function sends a message in the future specified by the user in the 
    dm specified by the user.

    Arguments:
        token (<string type>)    - token of the valid user
        dm_id (<int type>)    - id num of the dm to send the message
        message (<string type>)    - message to be sent
        time_sent (<int (unix timestamp) type>)    - time to send the message
        ...

    Exceptions:
        InputError  - Occurs when:
            - dm_id doesn't refer to a valid dm
            - the message is over 1000 characters
            - time_sent refers to a time in the past
            - 
        AccessError - Occurs when:
            - dm_id is valid but user is not a member of the dm
            - token is invalid

    Return Value:
        Returns {"message_id": message_id} if there is no errors and the message
        is bring threaded and sent later.
    """
    store = data_store.get()
    
    # Check if user token is valid
    user = search_user_token(token, store['users'])
    if user is None:
        raise AccessError(description='TOKEN INVALID')

    # Check if dm_id refers to a valid dm
    dm = find_dm(dm_id, store['dms'])
    if dm is None:
        raise InputError(description='Invalid dm_id')

    # Check if user is a member of the dm
    if is_a_member_dm(user['u_id'], dm['members']) is False:
        raise AccessError(description='You are not a member of this dm')

    # Check if length of message is < 1 character or > 1000 characters
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Message length must be between 1 and 1000 characters')

    # Get message_id
    message_id = get_new_message_id(store)

    # Get the current time
    rn = datetime.datetime.now()

    unix_rn = int(time.mktime(rn.timetuple()))

    # Check that the user didn't give us a time in the past
    if unix_rn > time_sent:
        raise InputError(description="You cannot send a message to the past, even though that would be pretty cool")
    
    # Get the unix time difference
    time_delta = time_sent - unix_rn

    # Make react dict
    react_dict = {  'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False}
    
    # Create message dictionary
    message_dict = {'message_id': message_id,
                    'u_id': user['u_id'],
                    'message': message,
                    'time_created': int(time.mktime(rn.timetuple())),
                    'reacts': [react_dict],
                    'is_pinned': False,
                    'dm_id': dm['dm_id']}
    
    # Threading for the appending the message into messages and dms
    # Addtional threading for saving to data
    messages_thread = threading.Timer(time_delta, add_to_list, args=(store['messages'], message_dict))
    dms_thread = threading.Timer(time_delta, add_to_list, args=(dm["messages"], message_dict))
    tagging_thread = threading.Timer(time_delta, tag_users_dm_msg, args=(message, user, dm, store))
    stats_user_thread = threading.Timer(time_delta, update_user_stat_dm, args=(user, store))
    stats_workspace_thread = threading.Timer(time_delta, update_workspace_stat_dm, args=(user, store))
    
    # Start the threads
    messages_thread.start()
    dms_thread.start()
    tagging_thread.start()
    stats_user_thread.start()
    stats_workspace_thread.start()
  
    return {
        'message_id': message_id
    }