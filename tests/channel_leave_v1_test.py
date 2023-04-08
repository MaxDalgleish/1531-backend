import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test whether an Access error is raised if the token is invalid
def test_invalid_token(clear_data):
    channel_leave = requests.post(config.url + "channel/leave/v1", 
                  json = {'token': invalid_token2(), "channel_id": 1})
    
    assert channel_leave.status_code == 403

# Test whether input error is raised when channel_id does not refer to a valid channel
def test_channel_id_invalid(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # User1 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # User1 leaves the channel
    channel_leave = requests.post(config.url + 'channel/leave/v1',
                                json = {'token': register_response1['token'],
                                        'channel_id': 5000})
    
    assert channel_leave.status_code == 400

# Test whether access error is raised if a channel id is valid but the user is not a member of the channel
def test_user_not_channel_member(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # User1 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # User 2 attempts to leave the channel
    channel_leave = requests.post(config.url + 'channel/leave/v1',
                                json = {'token': register_response2['token'],
                                        'channel_id': channel_response1['channel_id']})
    assert channel_leave.status_code == 403

# Test that everything is working properly
def test_remove_user(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Create a channel from the first user
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    requests.post(config.url + 'channel/leave/v1',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    # Checking channel_details
    details_response = requests.get(config.url + 'channel/details/v2',
                                params = {'token': register_response1['token'],
                                'channel_id': channel_response1['channel_id']})
    details_response = details_response.json()

    assert details_response == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

# Test of removing an owner from a channel
def test_owner_leave(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Create a channel from the first user
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})
    
    requests.post(config.url + 'channel/addowner/',
                json = {'token': register_response1['token'],
                        'channel_id': channel_response1['channel_id'],
                        'u_id': register_response3['auth_user_id']})

    requests.post(config.url + 'channel/leave/v1',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    # Checking channel_details
    details_response = requests.get(config.url + 'channel/details/v2',
                                params = {'token': register_response1['token'],
                                'channel_id': channel_response1['channel_id']})
    details_response = details_response.json()

    assert details_response == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                        'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

def test_remove_only_owner(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()
    

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Create a channel from the first user
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    requests.post(config.url + 'channel/leave/v1',
                json = {'token': register_response1['token'],
                        'channel_id': channel_response1['channel_id']})

    # Checking channel_details
    details_response = requests.get(config.url + 'channel/details/v2',
                                params = {'token': register_response2['token'],
                                'channel_id': channel_response1['channel_id']})
    details_response = details_response.json()

    assert details_response == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                                ], 
                                 'all_members':[
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {  
                                         'u_id': register_response3['auth_user_id'],
                                         'email': 'thirdemail@gmail.com',
                                         'name_first': 'Alex',
                                         'name_last': 'Steven',
                                         'handle_str': 'alexsteven',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }