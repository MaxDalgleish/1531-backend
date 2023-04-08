import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test where the token is invalid
def test_invalid_token(clear_data):
    channelinvite_response = requests.post(config.url + "channel/invite/v2", 
                  json = {'token': invalid_token2(), "channel_id": 1, "u_id": 1})
    
    assert channelinvite_response.status_code == 403

# Test if InputError is raised if channel_id is not valid
def test_channel_invite_v2_invalid_channel(clear_data):
    
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
    auth_user_id = register_response_data2["auth_user_id"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # Get response from channel invite
    invite_response = requests.post(config.url + 'channel/invite/v2',
                                    json={'token': token1,
                                          'channel_id': channel_id + 1,
                                          'u_id': auth_user_id})

    assert invite_response.status_code == 400

# Test if InputError is raised if u_id is already a member in the channel
def test_channel_invite_v2_already_in(clear_data):
    
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
    auth_user_id = register_response_data2["auth_user_id"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # User 1 invites user 2 into channel 1
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': token1,
                        'channel_id': channel_id,
                        'u_id': auth_user_id})

    # User 1 invites user 2 into channl 1 again
    invite_response = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id})

    assert invite_response.status_code == 400 

# Test if AccessError is raised if channel_id is valid but auth user not member
def test_channel_invite_v2_auth_not_member(clear_data):
    
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
    
    # Register user 3
    register_response3 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'panda@gmail.com',
                                            'password': 'panda12345',
                                            'name_first': 'panda', 
                                            'name_last': 'bear'})
    register_response_data3 = register_response3.json()
    auth_user_id = register_response_data3["auth_user_id"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    invite_response = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token2,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id})

    assert invite_response.status_code == 403

# Test if channel_invite returns empty dictionary on valid channel_id, auth_user_id
# and u_id
def test_channel_invite_v2_valid(clear_data): 
    
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
    auth_user_id = register_response_data2["auth_user_id"]
    
    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # Get invite response
    invite_response = requests.post(config.url + 'channel/invite/v2',
                                    json={'token': token1,
                                          'channel_id': channel_id,
                                          'u_id': auth_user_id})

    invite_response = invite_response.json()
    assert invite_response == {}

# Test whether channel_invite stores the correct user information
def test_channel_invite_v2_correctly(clear_data):
    
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
    auth_user_id = register_response_data2["auth_user_id"]
    
    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # User 1 invites user 2 into channel 1
    requests.post(config.url + 'channel/invite/v2',
                json={'token': token1,
                    'channel_id': channel_id,
                    'u_id': auth_user_id})

    # Gets channel details
    details_response = requests.get(config.url + 'channel/details/v2',
                                    params={'token': token1,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    # Make sure details is correct
    assert details_response == {
        'name': 'Channel 1',
        'is_public': False,
        'owner_members': [
            {
                'u_id': auth_user_id1,
                'email': 'testing1@gmail.com',
                'name_first': 'First',
                'name_last': 'Test',
                'handle_str': 'firsttest',
                'profile_img_url': config.url + "static/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': auth_user_id1,
                'email': 'testing1@gmail.com',
                'name_first': 'First',
                'name_last': 'Test',
                'handle_str': 'firsttest',
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': auth_user_id2,
                'email': 'derrick@gmail.com',
                'name_first': 'Derrick',
                'name_last': 'Doan',
                'handle_str': 'derrickdoan',
                'profile_img_url': config.url + "static/default.jpg"
            }
        ]
    }

# Test channel_invite works for multiple users
def test_channel_invite_v2_many_users(clear_data):
    
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
    
    # Register user 3
    register_response3 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'panda@gmail.com',
                                            'password': 'panda12345',
                                            'name_first': 'panda', 
                                            'name_last': 'bear'})
    register_response_data3 = register_response3.json()
    auth_user_id3 = register_response_data3['auth_user_id']
    
    # Register user 4
    register_response4 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'koala@gmail.com',
                                            'password': 'koala12345',
                                            'name_first': 'koala', 
                                            'name_last': 'koala'})
    register_response_data4 = register_response4.json()
    auth_user_id4 = register_response_data4['auth_user_id']

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id2})

    requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id3})  

    requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id4})

    # Gets channel details
    details_response = requests.get(config.url + 'channel/details/v2',
                                    params={'token': token1,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    # Make sure details is correct
    assert details_response == {
        'name': 'Channel 1',
        'is_public': False,
        'owner_members': [
            {
                'u_id': auth_user_id1,
                'email': 'testing1@gmail.com',
                'name_first': 'First',
                'name_last': 'Test',
                'handle_str': 'firsttest',
                'profile_img_url': config.url + "static/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': auth_user_id1,
                'email': 'testing1@gmail.com',
                'name_first': 'First',
                'name_last': 'Test',
                'handle_str': 'firsttest',
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': auth_user_id2,
                'email': 'derrick@gmail.com',
                'name_first': 'Derrick',
                'name_last': 'Doan',
                'handle_str': 'derrickdoan',
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': auth_user_id3,
                'email': 'panda@gmail.com',
                'name_first': 'panda',
                'name_last': 'bear',
                'handle_str': 'pandabear',
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': auth_user_id4,
                'email': 'koala@gmail.com',
                'name_first': 'koala',
                'name_last': 'koala',
                'handle_str': 'koalakoala',
                'profile_img_url': config.url + "static/default.jpg"
            }
        ]
    }

# Test channel_invite works to invite one user to multiple channels
def test_channel_invite_v2_multiple_channels(clear_data):
    
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
    auth_user_id2 = register_response_data2["auth_user_id"]
    
    # Create channel 1 and get channel id1
    channel_create_response1 = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data1 = channel_create_response1.json()
    channel_id1 = channel_create_response_data1["channel_id"]

    # Create channel 2 and get channel id2
    channel_create_response2 = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 2",
                                                  "is_public": True})
    channel_create_response_data2 = channel_create_response2.json()
    channel_id2 = channel_create_response_data2["channel_id"]
    
    # Create channel 3 and get channel id3
    channel_create_response3 = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 3",
                                                  "is_public": True})
    channel_create_response_data3 = channel_create_response3.json()
    channel_id3 = channel_create_response_data3["channel_id"]
    
    # Create channel 4 and get channel id4
    channel_create_response4 = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 4",
                                                  "is_public": True})
    channel_create_response_data4 = channel_create_response4.json()
    channel_id4 = channel_create_response_data4["channel_id"]
    
    invite_response1 = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id1,
                                       'u_id': auth_user_id2}) 

    invite_response2 = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id2,
                                       'u_id': auth_user_id2}) 

    invite_response3 = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id3,
                                       'u_id': auth_user_id2}) 

    invite_response4 = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id4,
                                       'u_id': auth_user_id2}) 
    
    assert invite_response1.status_code == 200
    assert invite_response2.status_code == 200
    assert invite_response3.status_code == 200
    assert invite_response4.status_code == 200

# Test if InputError is raised if user invited had been removed
def test_channel_invite_v2_removed_user(clear_data):
    
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
    # token2 = register_response_data2["token"]
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]
    
    # Removes user 2
    requests.delete(config.url + 'admin/user/remove/v1',
                    json={'token': token1,
                          'u_id': auth_user_id2})


    # Invite removed user 2
    invite_response = requests.post(config.url + 'channel/invite/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id,
                                       'u_id': auth_user_id2})

    assert invite_response.status_code == 400