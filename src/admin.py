'''
admin.py implementation

    Description:
        Functions for admin/user/remove/v1 and admin/userpermission/change/v1

    Functions:
        - Main functions:
            - admin/user/remove/v1
            - admin/userpermission/change/v1
        - Helper functions:
            - is_auth_user_global
            - is_user_valid
            - only_one_global
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import *
from src.message import edit_dm_message, edit_channel_message


def is_auth_user_global(auth_user_id, store):

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


def only_one_global(store):
    '''
    Function Description:
        Given a u_id and storage, checks if the user is the only global owner.

    Arguments:
        store (data)          - data storage

    Exceptions:
        N/A

    Return Value:
        Returns True on: only one global owner
        Returns False on: more than one global owner
    '''
    counter = 0
    for user in store['users']:
        if user['permission_id'] == 1:
            counter += 1
        if counter > 1:
            return False
    return True

def admin_user_permission_change_v1(token, u_id, permission_id):
    
    '''
    Function Description:
        Changes the user id's to the given permission_id, which is
        1: global owner
        2: regular user

    Arguments:
        token (str)                 - token of auth_user
        u_id (int)                  - users's id number
        permission_id (int)         - permission id number
    Exceptions:
        InputError      - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is the
                          only global owner and they are being demoted to a user
                        - Permission_id is invalid

        AccessError     - Occurs when auth_user_id is invalid 
                        - Auth_user is not a global owner

    Return Value:
        Returns {}
    '''

    store = data_store.get()
    # Find the user who had just registered
    found_user = search_user_token(token, store['users'])
    
    # If entered token does not belong to a user, raise inputerror
    if found_user is None:
        raise AccessError(description="Token entered is invalid")

    if is_auth_user_global(found_user['u_id'], store) is False:
        raise AccessError(description="Auth_user_id is not a global owner")

    if is_a_valid_uid(u_id, store) is None:
        raise InputError(description="U_id is not a valid user")

    if permission_id not in [1,2]:
        raise InputError(description="Permission_id is invalid")

    if permission_id != 1 and u_id == found_user['u_id']:
        if only_one_global(store) is True:
            raise InputError(description="Can not demote the only global owner")

    for user in store['users']:
        if user['u_id'] == u_id:
            user['permission_id'] = permission_id
            
    
    data_store.set(store)
    return {

    }


def admin_user_remove_v1(token, u_id):

    '''
    Function Description:
        Removes the user from the Streams. Removes them from all channels
        and list of users. Changes their message's contents to 'Removed User'.
        Retrieved profile is changed, so that name_first is 'Removed' and 
        name_last is 'user'. Makes emails and handle reusable.

    Arguments:
        token (str)                 - token of auth_user
        u_id (int)                  - users's id number

    Exceptions:
        InputError      - Occurs when u_id does not refer to a valid user
                        - Occurs when u_id refers to a user who is the
                          only global owner and they are being removed

        AccessError     - Occurs when auth_user_id is invalid 
                        - Auth_user is not a global owner

    Return Value:
        Returns {}
    '''

    store = data_store.get()
    
    # Check that the token is valid
    token_user = search_user_token(token, store['users'])
    # If entered token does not belong to a user, raise inputerror
    if token_user is None:
        raise AccessError(description="Token entered is invalid")

    if is_auth_user_global(token_user['u_id'], store) is False:
        raise AccessError(description="Auth_user_id is not a global owner")

    if is_a_valid_uid(u_id, store) is None:
        raise InputError(description="U_id is not a valid user")

    if u_id == token_user['u_id'] and only_one_global(store) is True:
        raise InputError(description="Can not remove the only global owner")


    # Change messages to 'Removed user'
    for message in store['messages']:
        if message['message_id'] != 0 and message['u_id'] == u_id:
            # If message is a dm message
            if 'dm_id' in message:
                dm = find_dm(message['dm_id'], store['dms'])
                edit_dm_message(message['message_id'], "Removed user", store, dm)

            # If the message is a channel message
            else:
                channel = get_channel(message['channel_id'], store)
                edit_channel_message(message['message_id'], "Removed user", store, channel)

    update_workspace_message(token_user, store)
    
    # Change necessary info in channels
    for channel in store['channels']:
        # Remove from owners
        for user in channel['owner_members']:
            if user['u_id'] == u_id:
                channel['owner_members'].remove(user)
        # Forced to leave from members
        for user in channel['all_members']:
            if user['u_id'] == u_id:
                channel['all_members'].remove(user)


    # Remove from dms
    for dm in store['dms']:
        # If owner, leave
        if dm['creator']['u_id'] == u_id:
            dm['creator'] == {}

        # Leave if member
        for member in dm['members']:
            if member['u_id'] == u_id:
                dm['members'].remove(member)

    
    # Change user info, keeping the u_id and change name    
    for user in store['users']:
        if user['u_id'] == u_id:
            user['email'] = ''
            user['password'] = ''
            user['handle_str'] = ''
            user['session_list'] = []
            user['permission_id'] = 0
            user['name_first'] = 'Removed'
            user['name_last'] = 'user'
            user['notifications'] = []
            user['reset_code'] = -1
            user['profile_img_url'] = ''

    data_store.set(store)
    return {

    }
