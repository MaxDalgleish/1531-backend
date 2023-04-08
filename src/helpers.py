''' 
helpers.py implementation

    Functions:

    - hash_password(input_string)
    - generate_new_session_id()
    - generate_jwt(username, session_id=None)
    - decode_jwt(encoded_jwt)
'''

# Import necessary libraries and files
import hashlib, uuid, jwt, datetime, time
from src.data_store import data_store

SECRET = 'reinforcerainstorm'

def hash_password(password):
    
    '''
    Hashes the input password with sha256
    Args:
        password ([string]): The input password to hash
    Returns:
        string: The hexidigest of the encoded password
    '''
    
    return hashlib.sha256(password.encode()).hexdigest()

def generate_new_session_id():
    
    '''
    Generates a new sequential session ID
    Args:
        None
    Returns:
        number: The next session ID
    '''
    
    # Generate a random uuid
    generated_session_id = str(uuid.uuid1())
    return generated_session_id

def generate_jwt(username, session_id):
    
    '''
    Generates a JWT using the global SECRET
    Args:
        username ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.
    Returns:
        string: A JWT encoded string
    '''
    
    # Note: HS256 is the signing algo, which signs the entire jwt to check wheter 
    # its valid
    # SECRET is required to decode the jwt, ensuring third parties cant generate jwt 
    # for this project
    return jwt.encode({'username': username, 'session_id': session_id}, 
                      SECRET, algorithm='HS256')

def decode_jwt(encoded_jwt):
    
    '''
    Decodes a JWT string into an object of the data
    Args:
        encoded_jwt ([string]): The encoded JWT as a string
    Returns:
        Object: An object storing the body of the JWT encoded string
    '''
    
    # returns the body of decoded jwt
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])

def timestamp():
    
    time_stamp = datetime.datetime.now()
    time_stamp = int(time.mktime(time_stamp.timetuple()))
    
    return time_stamp

# Helper function that searches for the user with the given email
def search_user_email(email, users):
    for user in users:
        # If a matching auth user id is found return user
        if user["email"] == email:
            return user
    return None

# Helper function that searchs for the user with the given token
def search_user_token(token, users):
    
    # Decode the token
    decoded_token = decode_jwt(token)
    
    for user in users:
        # If a matching auth user id is found return user
        for session_id in user['session_list']:
            if session_id == decoded_token['session_id']:
                return user
        # if decoded_token['session_id'] in user['session_list']:
        #     return user
    return None

def search_user_reset_code(reset_code, users):
    for user in users:
        # If a matching auth user id is found return user
        if user["reset_code"] == reset_code:
            return user
    return None

# Checks if given channel is valid
def is_channel_valid(channel_id, store):
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return True
    return False

# Gets channel dictionary from data_store
def get_channel(channel_id, store):
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return channel
    return None

# Checks if a given user is a member of a given channel
def is_a_member(auth_user_id, channel):
    for user in channel['all_members']:
        if user['u_id'] == auth_user_id:
            return True 
    return False

# Checks if a given uid is valid, removed users are invalid
def is_a_valid_uid(u_id, store):
    for user in store['users']:
        if user['u_id'] == u_id and user['email'] != "":
            return user
    return None

# Checks if a given uid exists, this includes removed users
def search_all_uids(u_id, store):
    for user in store['users']:
        if user['u_id'] == u_id:
            return user
    return None

# Checks if dm_id refers to a valid dm, if it is valid, returns dm dictionary
# if invalid, will return None
def find_dm(dm_id, dms):
    for dm in dms:
        if dm['dm_id'] == dm_id:
            return dm
    return None

# Checks if the given dm_id is valid
def is_dm_valid(dm_id, store):
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            return True
    return False

def is_a_member_dm(u_id, members):
    for member in members:
        if member['u_id'] == u_id:
            return True
    return False

# Helper function to filter users info
def filter_user_info(user):
    return {"u_id": user["u_id"],
            "email": user["email"],
            "name_first": user["name_first"],
            "name_last": user["name_last"],
            "handle_str": user["handle_str"],
            'profile_img_url': user["profile_img_url"]}

# Adds a notification to a user's notification list  
def send_notification(channel_id, dm_id, notif_msg, u_id):
    
    store = data_store.get()
    
    # Create individual notification dict
    notif_dict = {  
                    'channel_id': channel_id,
                    'dm_id': dm_id,
                    'notification_message': notif_msg
                }

    # Append the notif dict to user's notif list
    for user in store['users']:
        if user['u_id'] == u_id:
            user['notifications'].append(notif_dict)
    
    data_store.set(store)
    
def add_to_list(lst, msg):
    lst.append(msg)
    data_store.set
    
def update_user_stat_channel(user, store):
    
    time_stamp = timestamp()
    
    num_channels_joined = 0
    
    # Loop through all channels
    for channels in store['channels']:
        # In each channel, loop through the all_members list
        for member in channels['all_members']:
            # If the user is in the channel, iterate num_channels
            if member['u_id'] == user['u_id']:
                num_channels_joined += 1

    user['user_stats']['channels_joined'].append(
        {'num_channels_joined': num_channels_joined, 
         'time_stamp': time_stamp})

    data_store.set(store)
    
def update_user_stat_dm(user, store):
    
    time_stamp = timestamp()
    
    num_dms_joined = 0
    
    # Loop through all dms
    for dm in store['dms']:
        # In each channel, loop through the members list
        for member in dm['members']:
            # If the user is in the dm, iterate num_dms
            if member['u_id'] == user['u_id']:
                num_dms_joined += 1

    user['user_stats']['dms_joined'].append(
        {'num_dms_joined': num_dms_joined, 
         'time_stamp': time_stamp})

    data_store.set(store)
    
def update_user_stat_message(user, store):
    
    time_stamp = timestamp()
    
    num_messages_sent = 0
    
    # Loop through all messages
    for message in store['messages']:
        # If the user sent the message, iterate num_msg
        if message['u_id'] == user['u_id']:
            num_messages_sent += 1

    user['user_stats']['messages_sent'].append(
        {'num_messages_sent': num_messages_sent, 
         'time_stamp': time_stamp})

    data_store.set(store)
    
def num_dm_removed(dms):
        
    counter = 0
    for dm in dms:
        if dm['name'] == "":
            counter += 1
    return counter
    
def num_msg_removed(msgs):
    
    counter = 0
    for msg in msgs:
        if msg['time_created'] == 0:
            counter += 1
    return counter
    
def update_workspace_stat_channel(user, store):
    
    time_stamp = timestamp()
    
    num_channels_exist = len(store['channels'])

    store['stats']['channels_exist'].append({'num_channels_exist': num_channels_exist, 
                                        'time_stamp': time_stamp})

    data_store.set(store)
    
def update_workspace_stat_dm(user, store):
    
    time_stamp = timestamp()
    
    # Find the number of removed dms and thus number of existing dm
    num_removed_dm = num_dm_removed(store['dms'])
    num_dms_exist = len(store['dms']) - num_removed_dm

    store['stats']['dms_exist'].append({'num_dms_exist': num_dms_exist, 
                                        'time_stamp': time_stamp})

    data_store.set(store)
    
def update_workspace_message(user, store):
    
    time_stamp = timestamp()
    
    # Find the number of removed msgs and thus number of existing msgs
    num_removed_msg = num_msg_removed(store['messages'])
    num_messages_exist = len(store['messages']) - num_removed_msg
    
    store['stats']['messages_exist'].append({'num_messages_exist': num_messages_exist, 
                                        'time_stamp': time_stamp})

    data_store.set(store)

# Checks if auth_user has reacted to given message and changes 
# is_this_user_reacted accordingly
def change_is_this_user_reacted(messages_list, index, user):

    # If user has reacted
    if user['u_id'] in messages_list[index]['reacts'][0]['u_ids']:
        messages_list[index]['reacts'][0]['is_this_user_reacted'] = True
    
    # Else they have not reacted
    else:
        messages_list[index]['reacts'][0]['is_this_user_reacted'] = False
