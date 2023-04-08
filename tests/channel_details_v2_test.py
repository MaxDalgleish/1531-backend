import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test whether InputError is raised when a non-existent channel id is given
def test_channel_details_v2_id_non_existent(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Get response on channel/details/v2 with valid token but invalid channel_id
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token,
                                            'channel_id': 6000})

    # Check input error status code was returned
    assert details_response.status_code == 400

# Test whether AccessError status code is returned when an invalid token is entered
def test_channel_details_v2_invalid_user(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'cynthia', 
                                            'name_last': 'li'})
    register_response1 = register_response1.json()
    token1 = register_response1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'justin', 
                                            'name_last': 'son'})
    register_response2 = register_response2.json()
    token2 = register_response2["token"]

    # Create a channel and get response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'channel_one',
                                           'is_public': False})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Get response on channel/details/v2 with invalid token
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token2,
                                            'channel_id': channel_id})

    # Check AccessError status code is returned
    assert details_response.status_code == 403

# Test whether AcessError status code is returned when an invalid token and 
# invalid_channel_id are entered
def test_channel_details_v2_invalid_user_and_channel(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    register_response_data = register_response.json()
    
    token = register_response_data["token"]

    # Create a channel and get response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Staff',
                                           'is_public': False})
    channel_response_data = channel_response.json()
    
    channel_id = channel_response_data["channel_id"]

    # Register a second user
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'hamburger@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'hello', 
                                            'name_last': 'world'})
    register_response1 = register_response1.json()

    requests.post(config.url + "auth/logout/v1",
                  json={'token': register_response1['token']})

    # Get response on channel/details/v2 with invalid token and channel_id
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': register_response1['token'],
                                            'channel_id': channel_id + 1})
    

    # Check AccessError status code is returned
    assert details_response.status_code == 403

def test_channel_details_invalid_token(clear_data):
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    register_response = register_response.json()

    # Log user out
    requests.post(config.url + "auth/logout/v1",
                  json={'token': register_response['token']})

    # Logged out user calls channel_details
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': invalid_token1(),
                                            'channel_id': 1})

    assert details_response.status_code == 403


# Test whether AccessError is status code is returned when a user who is not a
# member of the channel calls channel_details
def test_channel_details_v2_not_a_member(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]

    # User 1 creates a channel
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'Staff',
                                           'is_public': False})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']

    # Get response on channel/details/v2 when a user who isn't a member calls it
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token2,
                                            'channel_id': channel_id})

    # Check that the status code was 403 (AccessError)
    assert details_response.status_code == 403

# Test whether a private channel returns the correct name, is_public, owner_members
# and all_members
def test_channel_details_v2_return_private_channel(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'cynthia', 
                                            'name_last': 'li'})
    register_response_data = register_response.json()
    auth_user_id = register_response_data['auth_user_id']
    token = register_response_data["token"]

    # Create a channel and store response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'validchannel',
                                           'is_public': False})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']
    
    # Get channel details response
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    assert details_response == {
                                    'name':'validchannel',
                                    'is_public': False,
                                    'owner_members': [
                                            {
                                                'u_id': auth_user_id,
                                                'email': "cynthia@gmail.com",
                                                'name_first': "cynthia",
                                                'name_last': "li",
                                                'handle_str': "cynthiali",
                                                'profile_img_url': config.url + "static/default.jpg"
                                            }
                                    ],
                                    'all_members':[
                                            {
                                                'u_id': auth_user_id,
                                                'email': "cynthia@gmail.com",
                                                'name_first': "cynthia",
                                                'name_last': "li",
                                                'handle_str': "cynthiali",
                                                'profile_img_url': config.url + "static/default.jpg"
                                            }
                                    ]
                                }

# Test whether a public channel returns the correct name, is_public, owner_members
# and all_members
def test_channel_details_v2_return_public_channel(clear_data):
    
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'cynthia', 
                                            'name_last': 'li'})
    register_response_data = register_response.json()
    auth_user_id = register_response_data['auth_user_id']
    token = register_response_data["token"]
    
    # Create a channel and store response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'validchannel',
                                           'is_public': True})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']

    # Get channel details response
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    assert details_response == {
                                    'name':'validchannel',
                                    'is_public': True,
                                    'owner_members': [
                                            {
                                                'u_id': auth_user_id,
                                                'email': "cynthia@gmail.com",
                                                'name_first': "cynthia",
                                                'name_last': "li",
                                                'handle_str': "cynthiali",
                                                'profile_img_url': config.url + "static/default.jpg"
                                            }
                                    ],
                                    'all_members':[
                                            {
                                                'u_id': auth_user_id,
                                                'email': "cynthia@gmail.com",
                                                'name_first': "cynthia",
                                                'name_last': "li",
                                                'handle_str': "cynthiali",
                                                'profile_img_url': config.url + "static/default.jpg"
                                            }
                                    ]
                                }

# Test whether a channel with many members returns the correct name, is_public,
# owner_members and all_members
def test_channel_details_v2_return_many_members(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'cynthia', 
                                            'name_last': 'li'})
    register_response_data1 = register_response1.json()
    auth_user_id1 = register_response_data1['auth_user_id']
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'justin', 
                                            'name_last': 'son'})
    register_response_data2 = register_response2.json()
    auth_user_id2 = register_response_data2['auth_user_id']
    
    # Register user 3
    register_response3 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'hello@gmail.com',
                                            'password': 'goodpassword',
                                            'name_first': 'hello', 
                                            'name_last': 'world'})
    register_response_data3 = register_response3.json()
    auth_user_id3 = register_response_data3['auth_user_id']

    # User 1 creates a new channel and response is saved
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'validchannel',
                                           'is_public': False})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']

    # User 1 invites user 2 and 3 to the channel
    requests.post(config.url + "channel/invite/v2",
                  json={'token': token1,
                        'channel_id': channel_id,
                        'u_id': auth_user_id2})

    requests.post(config.url + "channel/invite/v2",
                  json={'token': token1,
                        'channel_id': channel_id,
                        'u_id': auth_user_id3})

    # User 1 calls channel_details and response is saved
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token1,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    assert details_response == {
                                'name':'validchannel',
                                'is_public': False,
                                'owner_members': [
                                    {
                                        'u_id': auth_user_id1,
                                        'email': "cynthia@gmail.com",
                                        'name_first': "cynthia",
                                        'name_last': "li",
                                        'handle_str': "cynthiali",
                                        'profile_img_url': config.url + "static/default.jpg"
                                    }
                                                ],
                                'all_members':[
                                    {
                                        'u_id': auth_user_id1,
                                        'email': "cynthia@gmail.com",
                                        'name_first': "cynthia",
                                        'name_last': "li",
                                        'handle_str': "cynthiali",
                                        'profile_img_url': config.url + "static/default.jpg"
                                    },
                                    {
                                        'u_id': auth_user_id2,
                                        'email': "justin@gmail.com",
                                        'name_first': "justin",
                                        'name_last': "son",
                                        'handle_str': "justinson",
                                        'profile_img_url': config.url + "static/default.jpg"
                                    },
                                    {
                                        'u_id': auth_user_id3,
                                        'email': "hello@gmail.com",
                                        'name_first': "hello",
                                        'name_last': "world",
                                        'handle_str': "helloworld",
                                        'profile_img_url': config.url + "static/default.jpg"
                                    }
                                            ]
                            }