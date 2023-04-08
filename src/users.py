'''
users.py implementation

    Description:
        Implementations of user functions

    Functions:
        - Main functions:
            - users_all(token)
            - user_profile(token, u_id)
            - user_profile_setname(token, name_first, name_last)
            - user_profile_setemail(token, email)
            - user_profile_sethandle(token, handle)
            -user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
            - user_stats(token)
            - users_stats(token)
        - Helper functions:
            - handle_in_use(handle, store)
            - search_user_token(token,users)
            - filter_user_info(user)
            - search_all_uids(u_id, store) 
            - num_dm_removed(dms)
            - num_msg_removed(msgs)
'''

import re, datetime, time
from src.error import InputError, AccessError
from src.data_store import data_store
from src.helpers import search_user_token, \
                        filter_user_info, \
                        search_all_uids, \
                        num_dm_removed, \
                        num_msg_removed
from src.auth import handle_in_use
import requests
from PIL import Image
import urllib.request
from src import config

def users_all(token):

    '''
    Function Description:
        Retrieves  all users info and returns them in the below format:

    Arguments:
        token (string)      - token of the user

    Exceptions:
        AccessError - When the token is invalid

    Return Value:
        Returns: {'users':
                    [{"u_id": user["u_id"],
                    "email": user["email"],
                    "name_first": user["name_first"],
                    "name_last": user["name_last"],
                    "handle_str": user["handle_str"]}]
                }
    '''
    store = data_store.get()
    users = store["users"]
    res = []

    # If token is invalid
    if search_user_token(token, users) is None:
        raise AccessError(description='INVALID TOKEN')

    # Create a list of valid users
    for user in users:
        # If the user is a removed user, continue
        if user['email'] == '':
            continue
        filtered_info = filter_user_info(user)
        res.append(filtered_info)

    return {"users": res}

def user_profile(token, u_id):

    '''
    Function Description:
        Retrieves the user info with the corresponding u_id and returns it in the correct format

    Arguments:
        token (string)      - token of the user
        u_id(integer)       - u_id of the selected user

    Exceptions:
        InputError  - When the u_id is invalid
        AccessError - When the token is invalid

    Return Value:
        Returns {'user':
                    {"u_id": user["u_id"],
                    "email": user["email"],
                    "name_first": user["name_first"],
                    "name_last": user["name_last"],
                    "handle_str": user["handle_str"]}
                }   
    '''

    store = data_store.get()
    users = store["users"]

    # If token is invalid
    if search_user_token(token, users) is None:
        raise AccessError(description='INVALID TOKEN')
    
    # Check if u_id exists even if it is a removed user
    user = search_all_uids(u_id, store)
    if user is None:
        raise InputError(description='INVALID USER')

    filtered_info = filter_user_info(user)
    
    # Filter the user's info
    return {'user': filtered_info}

def user_profile_setname(token, name_first, name_last): 
     
    '''
    Function Description:
        Changes the current user's first and last name.
        

    Arguments:
        token (string)      - token of the user
        name_first(string)  - value of first name for changing
        name_last(string)   - value of last name for changing

    Exceptions:
        InputError  - When the first name and the last name
                      are not between 0-50 characters
        AccessError - When the token is invalid

    Return Value:
        Returns {}
    '''
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    dms = store['dms']

    # If token is invalid
    curr_user = search_user_token(token, users)
    if curr_user is None:
        raise AccessError(description='INVALID TOKEN')

    # If first name doesn't have a length between 0 and 50 characters
    if (len(name_first) > 50) or (name_first == ''):
        raise InputError("Please enter a valid first name")
    
    # If last name doesn't have a length between 0 and 50 characters
    if (len(name_last) > 50) or (name_last == ''):
        raise InputError("Please enter a valid last name")
    
    # Find the current user u_id
    curr_uid = curr_user['u_id']
    
    # Loop through to find the right user info to modify
    for user in users:
        if curr_uid == user["u_id"]:
            user["name_first"] = name_first
            user["name_last"] = name_last
    
    # Loop through channels to change the user's names 
    for channel in channels:
        for user in channel['owner_members']:
            if user['u_id'] == curr_uid:

                user["name_first"] = name_first
                user["name_last"] = name_last

        for user in channel['all_members']:
            if user['u_id'] == curr_uid:

                user["name_first"] = name_first
                user["name_last"] = name_last
                
    # Loop through dms to change the user's names 
    for dm in dms:
        for user in dm['members']:
            if user['u_id'] == curr_uid:

                user["name_first"] = name_first
                user["name_last"] = name_last

        if curr_uid == dm['creator']['u_id']:

            dm['creator']["name_first"] = name_first
            dm['creator']["name_last"] = name_last

    data_store.set(store)

    return {}

def user_profile_setemail(token, email): 
   
    '''
    Function Description:
        Changes the user email

    Arguments:
        token (string)      - token of the user
        email (string)      - the value of the email for changing

    Exceptions:
        InputError  - When the email is empty
                    - When the email is not an invalid email address
                    - When the email is already in use
        AccessError - When the token is invalid

    Return Value:
        Returns {}
    '''
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    dms = store['dms']

    # If token is invalid
    curr_user = search_user_token(token, users)
    if curr_user is None:
        raise AccessError(description='INVALID TOKEN')

    # Create a regular expression to check the email format
    regular_expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # If no email address was entered, raise inputerror
    if email == '':
        raise InputError(description="Please enter an email address")
    # If the email format was not valid, raise inputerror
    if not re.fullmatch(regular_expression, email):
        raise InputError(description="Please enter a valid email address")
    
    for user in users:
        # If existing users email is identical to the entered email, its a
        # duplicate, so raise inputerror
        if user['email'] == email:
            raise InputError(description="Duplicate email")

    # Find the current user u_id
    curr_uid = curr_user['u_id']
    
    # Loop through to find the right user info to modify
    for user in users:
        if curr_uid == user["u_id"]:
            user["email"] = email
    
    # Loop through channels to modify the user's email
    for channel in channels:
        for user in channel['owner_members']:
            if user['u_id'] == curr_uid:

                user["email"] = email

        for user in channel['all_members']:
            if user['u_id'] == curr_uid:

                user["email"] = email
                
    # Loop through dms to modify the user's email
    for dm in dms:
        for user in dm['members']:
            if user['u_id'] == curr_uid:

                user["email"] = email

        if curr_uid == dm['creator']['u_id']:

            dm['creator']["email"] = email

    data_store.set(store)

    return {}

def user_profile_sethandle(token, handle): 
    
    '''
    Function Description:
        Changes the current user's handle

    Arguments:
        token (string)      - token of the user
        handle (string)     - value of the handle for changing

    Exceptions:
        InputError  - When the handle is not between 3-20 characters
                    - When the handle contains non-alphanumeric characters
                    - WHen the handle is already in use
        AccessError - When the token is invalid

    Return Value:
        Returns 
    '''

    store = data_store.get()
    users = store['users']
    channels = store['channels']
    dms = store['dms']

    # If token is invalid
    curr_user = search_user_token(token, users)
    if curr_user is None:
        raise AccessError(description='INVALID TOKEN')

    # If the handle length is not between 3 and 20 characters raise an InputError
    if (len(handle) > 20) or (len(handle) < 3) or handle == '':
        raise InputError("Please enter a handle that is between 3 to 20 characters")
    
    # If the handle contains non_alphanumeric characters raise an InputError
    if handle.isalnum() is False:
        raise InputError("Please enter only alphanumeric characters")

    # If the handle is already in use raise an InputError
    if handle_in_use(handle, store) is True:
        raise InputError("This handle has alraedy been taken :(")

    # Find the current user u_id
    curr_uid = curr_user['u_id']
    
    # Loop through to find the right user info to modify
    for user in users:
        if curr_uid == user["u_id"]:
            user["handle_str"] = handle
    
    # Loop through channels to modify the user's handle
    for channel in channels:
        for user in channel['owner_members']:
            if user['u_id'] == curr_uid:

                user["handle_str"] = handle

        for user in channel['all_members']:
            if user['u_id'] == curr_uid:

                user["handle_str"] = handle
                
    # Loop through dms to modify the user's handle
    for dm in dms:
        for user in dm['members']:
            if user['u_id'] == curr_uid:

                user["handle_str"] = handle

        if curr_uid == dm['creator']['u_id']:

            dm['creator']["handle_str"] = handle

    data_store.set(store)

    return {}

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """
    Function uploads an image using a http url cropped to the user's specification as the 
    user's profile image. Additionally a profile image url is created so that the image (.jgp)
    file can be served locally.

    Arguments:
        token (<string type>)    - token of the user to verifiy the valid user
        img_url (<string type>)    - a valid http image url
        x_start (<int type>)    - cropping dimension starting point on the x-axis
        y_start (<int type>)    - cropping dimension starting point on the y-axis
        x_end (<int type>)    - cropping dimension ending point on the x-axis
        y_end (<int type>)    - cropping dimension ending point on the y-axis

    Exceptions:
        InputError  - Occurs when:
            - the img_url is a non-http or invalid url
            - incorrect cropping dimensions such as negative values
            - the x_start or y_start is larger than x_end or y_end respectively
            - if he file is not of jpg format
        AccessError - Occurs when :
            - the token is an invalid token

    Return Value:
        Returns {}
    """

    store = data_store.get()
    users = store['users']
    channels = store['channels']
    dms = store['dms']
    curr_user = search_user_token(token, users)
    ''
    # If token is invalid
    if curr_user is None:
        raise AccessError(description='INVALID TOKEN')

    curr_uid = curr_user['u_id']

    # Test if the url is valid on the web
    try:
        request = urllib.request.Request(img_url)
        request.get_method = lambda: 'HEAD'
    except ValueError as val_err:
        raise InputError(description="This is not a valid url") from val_err

    # Test if the url is http form
    try:
        urllib.request.urlopen(request)
    except urllib.request.HTTPError as error:
        raise InputError(description="This url is not valid") from error
    
    # If the image is of jpg and jpeg type
    if img_url.endswith((".jpg", ".jpeg")) == False:
        raise InputError(description="This type of image is not supported")

    # If the end dimensions are smaller than the starting dimensions
    if x_start > x_end or y_start > y_end or x_start < 0 or y_start < 0:
        raise InputError(description="Incorrect dimensions")
    
    # Generate user image profile name based on u_id and indexing
    image_file_path = "src/static/user" + str(curr_uid) + ".jpg"

    # Download and save the image
    urllib.request.urlretrieve(img_url, image_file_path)

    # Find out the image dimensions
    img = Image.open(image_file_path)
    width, height = img.size

    # If the cropping dimensions are out of range
    if x_end > width or y_end > height:
        raise InputError(description="Cropping dimensions out of range")

    # Crop the image and save
    cropped = img.crop((x_start, y_start, x_end, y_end))
    cropped.save(image_file_path)

    user_profile_img_url = config.url + "static/user" + str(curr_uid) + ".jpg"

    # Store the profile image url inside the users data
    for user in users:
        if user["u_id"] == curr_uid:
            user["profile_img_url"] = user_profile_img_url
    
    # Store the profile image_url inside the channel data
    for channel in channels:
        # Store the profile image_url inside the channel owner_members data
        for user in channel["owner_members"]:
            if user['u_id'] == curr_uid:
                user["profile_img_url"] = user_profile_img_url
        # Store the profile image_url inside the channel all_members data
        for user in channel['all_members']:
            if user['u_id'] == curr_uid:
                user["profile_img_url"] = user_profile_img_url

    # Store the profiel image url inside the dms data
    for dm in dms:
        # Store the profile image_url inside the dms all_members data
        for user in dm['members']:
            if user['u_id'] == curr_uid:
                user["profile_img_url"] = user_profile_img_url

        if dm['creator']['u_id'] == curr_uid:
            dm['creator']["profile_img_url"] = user_profile_img_url
    
    data_store.set(store)

    return {}
    
def user_stats(token):
    
    '''
    Function Description:
        Fetches the required statistics about this user's use of UNSW Streams.

    Arguments:
        token (string)      - token of the user

    Exceptions:
        AccessError         - When the token is invalid
        
    Return Value:
        Returns {user_stats} given valid token
    '''
    
    store = data_store.get()
    
    # Find the user given token
    registered_user = search_user_token(token, store['users'])
    
    # If entered token does not belong to a user, raise AccessError
    if registered_user is None:
        raise AccessError(description="Token entered is invalid")
    
    # Initialise all values to be zero
    num_channels_joined = 0
    num_dms_joined = 0
    num_messages_sent = 0
    involvement = 0.0
    
    # Loop through all channels
    for channels in store['channels']:
        # In each channel, loop through the all_members list
        for member in channels['all_members']:
            # If the user is in the channel, iterate num_channels
            if member['u_id'] == registered_user['u_id']:
                num_channels_joined += 1
    
    # Loop through all dms
    for dm in store['dms']:
        # In each channel, loop through the members list
        for member in dm['members']:
            # If the user is in the dm, iterate num_dms
            if member['u_id'] == registered_user['u_id']:
                num_dms_joined += 1
    
    # Loop through all messages
    for message in store['messages']:
        # If the user sent the message, iterate num_msg
        if message['u_id'] == registered_user['u_id']:
            num_messages_sent += 1
    
    # Find the number of removed dms and messages
    num_removed_dm = num_dm_removed(store['dms'])
    num_removed_msg = num_msg_removed(store['messages'])
    
    # Find the number of channels, dms and messages
    all_channels = len(store['channels'])
    all_dms = len(store['dms']) - num_removed_dm
    all_msgs = len(store['messages']) - num_removed_msg
    
    # Calculate numerator and denominator following the pseudocode
    numerator = num_channels_joined + num_dms_joined + num_messages_sent
    denominator = all_channels + all_dms + all_msgs
    
    if denominator == 0:
        involvement = 0.0    
    else:
        involvement = numerator / denominator
        
    if involvement > 1:
        involvement = 1.0
    
    # Save involvement
    registered_user['user_stats']['involvement_rate'] = involvement
    
    data_store.set(store)
    
    return {'user_stats': registered_user['user_stats']}

def is_in_a_channel(user, store):
    
    # Loop through all channels
    for channels in store:
        # In each channel, loop through the all_members list
        for member in channels['all_members']:
            # If the user is in the channel, iterate num_channels
            if member['u_id'] == user['u_id']:
                return True
    return False
            
def is_in_a_dm(user, store):
    
    # Loop through all dms
    for dm in store:
        # In each channel, loop through the members list
        for member in dm['members']:
            # If the user is in the dm, iterate num_dms
            if member['u_id'] == user['u_id']:
                return True
    return False

def users_stats(token):
    
    '''
    Function Description:
        Fetches the required statistics about the use of UNSW Streams.

    Arguments:
        token (string)      - token of the user

    Exceptions:
        AccessError         - When the token is invalid
        
    Return Value:
        Returns {workspace_stats} given valid token
    '''
    
    store = data_store.get()
    
    # Find the user given token
    registered_user = search_user_token(token, store['users'])
    
    # If entered token does not belong to a user, raise AccessError
    if registered_user is None:
        raise AccessError(description="Token entered is invalid")
    
    # Initialise values to be 0
    utilisation = 0.0
    num_users_in_none = 0
    removed_users = 0
    
    # Loop through to find the number of removed users and none users
    for user in store['users']:
        # If the user is not removed
        if user['permission_id'] != 0:
            # Check if they're a part of a channel or dm
            if is_in_a_channel(user, store['channels']) == False\
                and is_in_a_dm(user, store['dms']) == False:
                num_users_in_none += 1
        # Otherwise, user is removed
        else:
            removed_users += 1

    # Calculate numerator and denominator and utilisation according to the pseudocode
    numerator = len(store['users']) - removed_users - num_users_in_none
    denominator = len(store['users']) - removed_users
    utilisation = numerator / denominator
    
    registered_user['workspace_stats'] = store['stats']
    
    registered_user['workspace_stats']['utilization_rate'] = utilisation
    
    data_store.set(store)
    
    return {'workspace_stats': registered_user['workspace_stats']}

