import pytest
import requests
from src import config
from tests.test_helpers import invalid_token3

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test where the token is invalid
def test_invalid_token(clear_data):
    addowner_response = requests.post(config.url + "channel/join/v2", 
                  json = {'token': invalid_token3(), "channel_id": 1})
    
    assert addowner_response.status_code == 403


# test whether InputError is raised if channel_id does not refer to a valid channel_id
def test_channel_join_v2_invalid_channel(clear_data):
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token,
                                           'name': 'Channel 1',
                                           'is_public': True})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Joins channel, with invalid channel_id
    join_response = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token,
                                       'channel_id': channel_id + 1})

    assert join_response.status_code == 400

# Test whether InputError is raised if authorised user is already a member of
# the channel
def test_channel_join_v2_already_member(clear_data):
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token,
                                           'name': 'Channel 1',
                                           'is_public': True})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Joins channel, but user had created the channel
    join_response = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token,
                                       'channel_id': channel_id})

    assert join_response.status_code == 400

# Test whether AccessError is raised if channel is private and user is not a
# member or global owner
def test_channel_join_v2_private_channel(clear_data):
    
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token1,
                                           'name': 'Channel 1',
                                           'is_public': False})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Joins channel, but channel is private
    join_response = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                       'channel_id': channel_id})

    assert join_response.status_code == 403

# Test whether global owner can join a private channel
def test_channel_join_v2_global_owner(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]

    # 2nd user creates a private channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token2,
                                           'name': 'Channel 1',
                                           'is_public': False})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']
    
	# 1st user(global_owner) joins channel
    join_response = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id})

    assert join_response.status_code == 200

# Test whether empty dictionary is returned on valid channel_id and valid token
def test_channel_join_v2_correct_return(clear_data):
    
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token1,
                                           'name': 'Channel 1',
                                           'is_public': True})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Joins channel
    join_response = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                       'channel_id': channel_id})
    join_response = join_response.json()

    assert join_response == {}

# Test whether channel_join stores the correct user information in all_members
def test_channel_join_v2_stored_correctly(clear_data):
    
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    auth_user_id1 = register_response_data1['auth_user_id']
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    auth_user_id2 = register_response_data2['auth_user_id']
    token2 = register_response_data2["token"]

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token1,
                                           'name': 'Channel 1',
                                           'is_public': True})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Joins channel
    requests.post(config.url + 'channel/join/v2',
                 json={'token': token2,
                       'channel_id': channel_id})

    # Gets channel details
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token1,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    # Make sure details is correct
    assert details_response == {
        'name': 'Channel 1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': auth_user_id1,
                'email': "testing1@gmail.com",
                'name_first': "First",
                'name_last': "Test",
                'handle_str': "firsttest",
                'profile_img_url': config.url + "static/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': auth_user_id1,
                'email': "testing1@gmail.com",
                'name_first': "First",
                'name_last': "Test",
                'handle_str': "firsttest",
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': auth_user_id2,
                'email': "derrick@gmail.com",
                'name_first': "Derrick",
                'name_last': "Doan",
                'handle_str': "derrickdoan",
                'profile_img_url': config.url + "static/default.jpg"
            }
        ]
    }
