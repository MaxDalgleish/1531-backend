''' 
auth.py implementation

    Functions:

    - check_login(email, password, store)
    - auth_login_v1(email, password)
    - handle_in_use(handle, store)
    - auth_register_v1(email, password, name_first, name_last)
'''

import re, random, smtplib, datetime, time
# Import other required files
from src.data_store import data_store
from src.error import InputError, AccessError
from src import config
from .helpers import *

def check_login(email, password, store):

    '''
    Function Description:
        Given a registered user's email, password and storage, returns info on
        whether user exists in storage.

    Arguments:
        email (string)          - user's email
        password (string)       - user's password
        store (data)            - data storage

    Exceptions:
        N/A

    Return Value:
        Returns user on: user found in storage
        Returns None on: user not found in storage
    '''

    for user in store['users']:
        # If the entered email and hashed password matches, return user
        if (user['email'] == email) and (user['password'] == password):
            return user
    # Otherwise, details did not match, return None
    return None

def auth_login_v1(email, password):

    '''
    Function Description:
        Given a registered user's email and password, returns their
        auth_user_id.

    Arguments:
        email (string)          - user's email
        password (string)       - user's password

    Exceptions:
        InputError  - Occurs when email entered does not belong to any user
                    - Occurs when password is not correct

    Return Value:
        Returns {auth_user_id} on: correct email and password
    '''

    store = data_store.get()
    # Find the user who had just logged in
    logged_in_user = search_user_email(email, store['users'])
    
    # If entered email does not belong to a user, raise inputerror
    if logged_in_user is None:
        raise InputError(description="Email entered does not belong to a user")        
        
    # Generate a new session id and append
    session_id = generate_new_session_id()
    logged_in_user['session_list'].append(session_id)
    # Generate a token and store
    generated_token = generate_jwt(logged_in_user['email'], session_id)
    logged_in_user['token'] = generated_token
    
    # Generate a hashed password using hash helper function and convert it to hex
    hashed_password = hash_password(password)
    
    # Check if a user exists with the hashed password and email combination
    user = check_login(email,hashed_password, store)

    # If no user has that password and email combination
    if user is None:
        raise InputError("Please enter a valid email and password")

    data_store.set(store)
    # If a user exists with the email and password combination, return their
    # user_id and token
    return {
        'token': generated_token,
        'auth_user_id': user['u_id']
    }

def handle_in_use(handle, store):

    '''
    Function Description:
        Given a registered user's handle and storage, returns boolean whether
        user is in store.

    Arguments:
        handle (string)          - user's handle
        store (data)             - data storage

    Exceptions:
        N/A

    Return Value:
        Returns True on: user found in storage
        Returns False on: user not found in storage
    '''

    for user in store['users']:
        # If the handle is taken by another user, return true
        if user['handle_str'] == handle:
            return True
    # Otherwise, return false
    return False

def auth_register_v1(email, password, name_first, name_last):

    '''
    Function Description:
        Given a user's first and last name, email address, and password, create
        a new account for them and return a new auth_user_id. An alphanumeric
        handle is generated as a concatenation of the user's first and last name
        which may have an index if there are duplicates.

    Arguments:
        email (string)          - user's email
        password (string)       - user's password
        name_first(string)      - user's first name
        name_last(string)       - user's last name

    Exceptions:
        InputError  - Occurs when email is invalid
                    - Occurs when there is no email
                    - Occurs when the email is a duplicate
                    - Occurs when the password is less than 6 characters
                    - Occurs when the name_first is none or greater than 50
                    characters
                    - Occurs when the name_last is none or greater than 50
                    characters
                    - Occurs when name_last and name_first both do not include
                    any alphanumeric characters

    Return Value:
        Returns {auth_user_id} on: valid email, password, name_first and
        name_last
    '''

    store = data_store.get()

    # Create a regular expression to check the email format
    regular_expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # If no email address was entered, raise inputerror
    if email == '':
        raise InputError("Please enter an email address")

    # If the email format was not valid, raise inputerror
    if not re.fullmatch(regular_expression, email):
        raise InputError("Please enter a valid email address")

    for users in store['users']:
        # If existing users email is identical to the entered email, its a
        # duplicate, so raise inputerror
        if users['email'] == email:
            raise InputError("Duplicate email")

    # If the password was not entered or it contained less than 6 characters,
    # raise inputerror
    if (len(password) < 6) or (password == ''):
        raise InputError("Please enter a valid password")

    # If first name didnt have a length between 0 and 50, raise inputerror
    if (len(name_first) > 50) or (name_first == ''):
        raise InputError("Please enter a valid first name")

    # If last name didnt have a length between 0 and 50, raise inputerror
    if (len(name_last) > 50) or (name_last == ''):
        raise InputError("Please enter a valid last name")

    # The handle is created by concatenating the lowercase first and last names
    handle = name_first.lower() + name_last.lower()

    # Remove all non alphanumeric chars from the handle
    handle = re.sub(r'[^a-zA-Z0-9]', '', handle)

    # If the handle includes no non_alphanumeric characters, raise an InputError
    if handle == '':
        raise InputError("Please enter a name that includes at least one alpha-numeric character")

    # If the handle length is over 20 characters, its truncated to 20
    if len(handle) > 20:
        handle = handle[0:20]
    # If the handle is in use already
    if handle_in_use(handle, store) == True:
        counter = 0
        # loop until there is a new handle
        while handle_in_use((handle + str(counter)), store) == True:
            counter += 1
        # when false, make the final handle
        handle = handle + str(counter)
        
    # Generate timestamp
    time_stamp = datetime.datetime.now()
    time_stamp = int(time.mktime(time_stamp.timetuple()))
    
    # Create default user stats and workspace stats
    user_stats = {'channels_joined': [{'num_channels_joined': 0, 
                                       'time_stamp': time_stamp}],
                  'dms_joined': [{'num_dms_joined': 0, 
                                  'time_stamp': time_stamp}],
                  'messages_sent': [{'num_messages_sent': 0, 
                                     'time_stamp': time_stamp}],
                  'involvement_rate': 0}
    
    workspace_stats = {'channels_exist': [{'num_channels_exist': 0, 
                                           'time_stamp': time_stamp}],
                       'dms_exist': [{'num_dms_exist': 0, 
                                      'time_stamp': time_stamp}],
                       'messages_exist': [{'num_messages_exist': 0, 
                                           'time_stamp': time_stamp}],
                       'utilization_rate': 0}

    # Generate a hashed password using hash helper function and convert it to hex
    hashed_password = hash_password(password)

    # The new id is created from the number of elements in storage plus one
    u_id = len(store['users']) + 1

    # Generate a new session id
    session_id = generate_new_session_id()

    # Generate a new token
    generated_token = generate_jwt(email, session_id)
    
    # Create user_dictionary
    user_dictionary = {'u_id': u_id, 
                       'email': email, 
                       'password': hashed_password,
                       'name_first': name_first, 
                       'name_last': name_last,
                       'handle_str': handle, 
                       'session_list': [session_id],
                       'permission_id': 2, 
                       'reset_code': -1, 
                       'notifications': [], 
                       'user_stats': user_stats,
                       'workspace_stats': workspace_stats,
                       'profile_img_url': config.url + "static/default.jpg"}

    # If u_id is 1, give that user the global owner status
    if u_id == 1:
        user_dictionary['permission_id'] = 1

    # The valid information is appended
    store['users'].append(user_dictionary)  
    
    if len(store['stats']) == 0:
        store['stats'] = workspace_stats

    data_store.set(store)
    
    return {
        'token': generated_token,
        'auth_user_id': u_id
    }

def auth_logout(token):
    
    '''
    Function Description:
        Given an active token, invalidates the token to log the user out.

    Arguments:
        token (str)             - authorisation hash

    Exceptions:
        NA

    Return Value:
        Returns {} on: valid token
    '''

    store = data_store.get()
    # Find the user who had just registered
    registered_user = search_user_token(token, store['users'])

    # If entered token does not belong to a user, raise AccessError
    if registered_user is None:
        raise AccessError(description="Token entered is invalid")
        
    decoded_token = decode_jwt(token)
    # Search through all users
    for user in store['users']:
        if decoded_token['session_id'] in user['session_list']:
            user['session_list'].remove(decoded_token['session_id'])

    data_store.set(store)
    return {}

def auth_password_reset_request(email):
    
    '''
    Function Description:
        Given an email address, if the user is a registered user, sends them an
        email containing a specific secret code. When a user requests a password
        reset, they're logged out of all current sessions.

    Arguments:
        email (str)             - users email

    Exceptions:
        NA

    Return Value:
        Returns {} on: valid email
    '''
    
    store = data_store.get()
    
    # Find the user given the email address
    found_user = search_user_email(email, store['users'])
    
    # If the user was not found, return
    if found_user is None:
        return {}
    
    # Generate a random 6 digit interger
    reset_code = random.randint(000000,999999)
    
    # Log user out of all current sessions and save the reset code
    found_user['session_list'] = []
    found_user['reset_code'] = reset_code
    
    # Use smtp class and specify gmail and port number
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        
        # Identify with mail server then encrypt traffic
        smtp.ehlo()
        smtp.starttls()
        # Re-identify with encrypted connection
        smtp.ehlo()
        
        # Login to the mail server
        smtp.login("davidphilips0203@gmail.com", "worldpeace2021")
        
        subject = 'Password Change Request'
        body = f'Your reset code is {reset_code}'
        msg = f'subject: {subject}\n\n{body}'
        
        # Send the message to the receiver
        smtp.sendmail("davidphilips0203@gmail.com", email, msg)
    
    data_store.set(store)
    return {}

def auth_password_reset(reset_code, new_password):
    
    '''
    Function Description:
        Given a reset code for a user, set that user's new password to the 
        password provided.

    Arguments:
        reset_code (str)             - secret code
        new_password (str)           - new password for the user

    Exceptions:
        InputError - Occurs when reset_code is invalid
                   - Occurs when new_password is less than 6 characters long

    Return Value:
        Returns {} on: valid reset code and new password
    '''
    
    store = data_store.get()
    
    # If new password has length less than 6, raise inputerror
    if len(new_password) < 6:
        raise InputError(description='Please enter a valid password')
    
    # Find the user given the reset code
    found_user = search_user_reset_code(reset_code, store['users'])
    
    # If user is not found given the reset code, code is invalid
    if found_user is None:
        raise InputError(description='Reset code is invalid')
    
    # Otherwise, code is valid
    else: # pragma: no cover
        # Generate a new hashed password using hash function and update it
        found_user['password'] = hash_password(new_password)
        # Set reset code to default again
        found_user['reset_code'] = -1

        data_store.set(store)
        return {}
