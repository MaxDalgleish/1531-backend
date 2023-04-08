'''
dm.py implementation

    Description:
        Functions implementation of dm

    Functions:
        - Main functions:
            - dm_create(token, u_ids)
            - dm_list(token)
            - dm_messages(token, dm_id, start)
            - dm_remove(token, dm_id)
            - dm_details(token, dm_id)
            - dm_leave(token, dm_id)
        - Helper functions:
            - search_user_token
            - is_a_valid_uid
            - find_dm
            - is_a_member_dm
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import search_user_token, \
                        is_a_valid_uid, \
                        find_dm, \
                        is_a_member_dm, \
                        send_notification, \
                        update_user_stat_dm, \
                        update_workspace_stat_dm, \
                        change_is_this_user_reacted, \
                        update_workspace_stat_dm
from .message import delete_dm_message

def dm_create(token, u_ids):
    '''
    Function Description:
        Create a dm with the specified users

    Arguments:
        token (str)             - authorisation hash
        u_ids (list)            - list of user_ids

    Exceptions:
        InputError              - When any user_id does not refer to a valid user

        AccessError             - Occurs when Token is invalid

    Return Value:
        Returns {dm_id}
    '''
    
    store = data_store.get()
    # Find the owner member given the token
    owner_member = search_user_token(token, store['users'])
    
    # If the owner member is not found, raise accesserror
    if owner_member is None:
        raise AccessError(description="INVALID TOKEN")
    
    # Loop through the given list of u_ids, and if any u_id is invalid, raise
    # inputerror
    for u_id in u_ids:
        if is_a_valid_uid(u_id, store) == None:
            raise InputError(description="u_id is invalid")
    
    # Create empty lists
    list_of_handles = []
    members = []

    # Create a user dictionary for creator containing all necessary information
    creator = {'u_id': owner_member['u_id'],
               'email': owner_member['email'],
               'name_first': owner_member['name_first'],
               'name_last': owner_member['name_last'],
               'handle_str': owner_member['handle_str'],
               'profile_img_url': owner_member['profile_img_url']}
    
    # Append the creator to both all members and owner members
    members.append(creator)

    # Append the creators handle to the list
    list_of_handles.append(owner_member['handle_str'])
    
    # Loop through all u_id
    for u_id in u_ids:
        
        # Finds user given the uid, and append its handle to the list
        found_user = is_a_valid_uid(u_id, store)
        list_of_handles.append(found_user['handle_str'])
        
        # Create a user dictionary containing all necessary information
        user = {'u_id': found_user['u_id'],
                'email': found_user['email'],
                'name_first': found_user['name_first'],
                'name_last': found_user['name_last'],
                'handle_str': found_user['handle_str'],
                'profile_img_url': found_user['profile_img_url']}
        
        # Append the user info to all members
        members.append(user)
    
    # Sort the list of handles alphabetically and join them separated by comma
    # and a space
    name = ', '.join(sorted(list_of_handles))

    # Generate dm_id from the length of dms list
    dm_id = len(store['dms']) + 1
    
    # Send a notification to each user in u_ids list
    notif_message = f"{owner_member['handle_str']} added you to {name}"
    for u_id in u_ids:
        send_notification(-1, dm_id, notif_message, u_id)
    
    # Create dms structure containing necessary information
    dm = {'dm_id': dm_id,
          'name': name,
          'messages': [],
          'creator': creator,
          'members': members}
    
    # Append the dm
    store['dms'].append(dm)

    # Find the members whose info has to be updated for stats
    members_to_be_updated = []
    for user in store['users']:
        for member in members:
            if user['u_id'] == member['u_id']:
                members_to_be_updated.append(user)
    
    # Update all members for stat            
    for member in members_to_be_updated:
        update_user_stat_dm(member, store)
    update_workspace_stat_dm(member, store)
    
    data_store.set(store)
    return {
        'dm_id': dm_id
    }

def dm_list(token):
    '''
    Function Description:
        Return the list of DMs that the user is a member of

    Arguments:
        token (str)             - authorisation hash

    Exceptions:
        AccessError             - Occurs when Token is invalid

    Return Value:
        Returns {dms}
    '''
    
    store = data_store.get()
    
    # Find the user given the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description="INVALID TOKEN")

    # Create an empty list to return
    return_dms = []
    
    # Loop through the dms
    for dms in store['dms']:
        # Loop through all members
        for member in dms['members']:
            # If the auth_user's id is found in all_members
            if member['u_id'] == found_user['u_id']:
                # Append the dm_id and name dict to list
                return_dms.append({'dm_id': dms['dm_id'],
                                   'name': dms['name']})

    return {
        'dms': return_dms
    }
    
def dm_messages(token, dm_id, start):
    '''
    Function Description:
        return a dictionary with the messages present in a channel

    Arguments:
        token (str)             - authorisation hash
        dm_id (int)             - id of the dm
        start (int)             - index of the messages

    Exceptions:
        InputError              - When dm_id does not refer to any DM
                                - Start is greater than the total number of 
                                messages in the channel

        AccessError             - Occurs when Token is invalid
                                - when dm_id is valid and the authorised user is 
                                not a member of the DM

    Return Value:
        Returns {messages, start, end}
    '''
    
    store = data_store.get()
    
    # Find the user given the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description="INVALID TOKEN")
    
    # Find the dm given the dm_id
    found_dm = find_dm(dm_id, store['dms'])
    
    # If dm is not found, raise inputerror 
    if found_dm is None:
        raise InputError(description="Invalid dm_id")
    
    # If dm is found, but the member is not in the DM, raise accesserror
    if is_a_member_dm(found_user['u_id'], found_dm['members']) is False:
        raise AccessError(description="User is not a member of the DM")

    dm_messages = found_dm['messages']
    # Get list of dms dictionaries and find the total number of dms
    total_messages_in_dm = len(dm_messages)
    
    # If start is greater than the total number of dms, raise inputerror
    if start > total_messages_in_dm:
        raise InputError(description="Start is greater than the total number of messages")
    
    # Create a list of messages to return
    messages_list = []
    
    # If there are less than 50 dm messages left to load
    if start + 50 >= total_messages_in_dm:
        
        # Find number of dm messages left
        messages_left = total_messages_in_dm - start

        # Append the remaining messages to message_list
        for num in range(0, messages_left):
            messages_list.append(dm_messages[num])
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
    
    # Append the remaining messages to message_list
    index = 0
    for num in range(start, start + 50):
        messages_list.append(dm_messages[total_messages_in_dm - num - 1])
        change_is_this_user_reacted(messages_list, index, found_user)
        index += 1

    data_store.set(store)                    
    return {
        'messages': messages_list,
        'start': start,
        'end': start + 50
    }

def dm_remove(token, dm_id):
    '''
    Function Description:
        Remove an existing DM

    Arguments:
        token (str)             - authorisation hash
        dm_id (int)             - id of the dm

    Exceptions:
        InputError              - When dm_id does not refer to any DM

        AccessError             - Occurs when Token is invalid
                                - when dm_id is valid and the authorised user is
                                not the original creator of the DM

    Return Value:
        Returns {}
    '''
    
    store = data_store.get()
    
    # Find the user given the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description="INVALID TOKEN")
    
    # Find the dm given the dm_id
    found_dm = find_dm(dm_id, store['dms'])
    
    # If dm is not found, raise inputerror 
    if found_dm is None:
        raise InputError(description="Invalid dm_id")
    
    # If found dm creator or memebers is empty, its a removed dm, so raise inputerror
    if found_dm['creator'] == {} and found_dm['members'] == []:
        raise InputError(description="Invalid dm_id")
    
    # If dm is found, but the member is not a creator, raise accesserror
    if found_user['u_id'] != found_dm['creator']['u_id'] :
        raise AccessError(description="User is not the creator of the DM")
    
    # Find the members whose info has to be updated for stats
    members_to_be_updated = []
    for user in store['users']:
        for member in found_dm['members']:
            if user['u_id'] == member['u_id']:
                members_to_be_updated.append(user)
    
    # Remove everything but keep dm_id
    found_dm['creator'] = {}
    found_dm['members'] = []
    found_dm['name'] = ""
    
    for message in found_dm['messages']:
        delete_dm_message(message['message_id'], store, found_dm)
    
    # Update required members info for stats    
    for member in members_to_be_updated:
        update_user_stat_dm(member, store)
    update_workspace_stat_dm(member, store)
    
    data_store.set(store)
    return {}

def dm_details(token, dm_id):
    '''
    Function Description:
        Provide basic details about the given dm

    Arguments:
        token (str)             - authorisation hash
        dm_id (int)             - id of the dm

    Exceptions:
        InputError              - When dm_id does not refer to any dm

        AccessError             - Occurs when Token is invalid
                                - when dm_id is valid and the authorised user is
                                not a member of the DM

    Return Value:
        Returns {name, members}
    '''
    
    store = data_store.get()
    
    # Find the user given the token
    found_user = search_user_token(token, store['users'])
    
    # If user is not found, raise accesserror
    if found_user is None:
        raise AccessError(description="INVALID TOKEN")
    
    # Find the dm given the dm_id
    found_dm = find_dm(dm_id, store['dms'])
    
    # If dm is not found, raise inputerror 
    if found_dm is None:
        raise InputError(description="Invalid dm_id")
    
    # If dm is found, but the member is not in the DM, raise accesserror
    if is_a_member_dm(found_user['u_id'], found_dm['members']) is False:
        raise AccessError(description="User is not a member of the DM")

    return {'name': found_dm['name'],
            'members': found_dm['members']}

def dm_leave(token, dm_id):
    '''
    Function Description:
        User is removed from the DM

    Arguments:
        token (str)             - authorisation hash
        dm_id (int)             - id of the dm

    Exceptions:
        InputError              - When dm_id does not refer to any dm

        AccessError             - Occurs when Token is invalid
                                - when dm_id is valid and the authorised user is
                                not a member of the DM

    Return Value:
        Returns {}
    '''
    
    store = data_store.get()

    # Find the user given the token
    found_user = search_user_token(token, store['users'])

    # If user is not found, raise Access Error
    if found_user is None:
        raise AccessError(description='INVALID TOKEN')

    # Find the dm given the dm_id
    found_dm = find_dm(dm_id, store['dms'])

    # If dm is not found, raise Inputerror
    if found_dm is None:
        raise InputError(description='Invalid dm_id')

    # If dm is found, but the member is not in the DM, raise Access Error
    if is_a_member_dm(found_user['u_id'], found_dm['members']) is False:
        raise AccessError(description='User is not a member of the DM')
    
    # Removing user from the dm
    for member in found_dm['members']:
        if member['u_id'] == found_user['u_id']:
            found_dm['members'].remove(member)
    
    # Removing an owner from the dm
    owner = found_dm['creator']
    if owner['u_id'] == found_user['u_id']:
        found_dm['creator'] = {}
    
    # Update the user for stats
    update_user_stat_dm(found_user, store)
    
    data_store.set(store)

    return {}
    