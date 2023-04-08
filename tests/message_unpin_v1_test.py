import pytest
import requests
from src import config
from src.error import AccessError, InputError
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
def register_user_1():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'password123',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    return register_response.json()

def register_user_2():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'password123456',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    return register_response.json()

def register_user_3():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Derrick@gmail.com',
                                            'password': 'password000',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    return register_response.json()

# Test if invalid token raises an AccessError
def test_message_unpin_invalid_token(clear_data):

    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # Send a dm
    send_response = requests.post(config.url + "message/senddm/v1",
                                  json={'token': token1,
                                        'dm_id': dm_create_response['dm_id'],
                                        'message': "Come to life"})
    send_response = send_response.json()
    
    # Pin the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response['message_id']})
    
    # Unpin the dm given an invalid token
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': invalid_token1(),
                                         'message_id': send_response['message_id']})

    assert unpin_response.status_code == AccessError.code
    
# Test whether InputError is raised given invalid message id for channel
def test_message_unpin_channel_invalid_id(clear_data):
    
    # Register a user and save response
    register_response = register_user_1()
    token = register_response['token']

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Zoom',
                                           'is_public': False})
    channel_response = channel_response.json()

    # Send a message in the channel
    send_response = requests.post(config.url + "message/send/v1",
                                  json={'token': register_response['token'],
                                        'channel_id': channel_response['channel_id'],
                                        'message': "Meeting"})
    send_response = send_response.json()
    
    # Pin the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token,
                        'message_id': send_response['message_id']})

    # Unpin the message given an invalid message id in channel
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': token,
                                         'message_id': 0})
    
    assert unpin_response.status_code == InputError.code

# Test whether InputError is raised given invalid message id for dm
def test_message_unpin_dm_invalid_id(clear_data):

    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # Send a dm message
    send_response = requests.post(config.url + "message/senddm/v1",
                                  json={'token': token1,
                                        'dm_id': dm_create_response['dm_id'],
                                        'message': "French Toast"})
    send_response = send_response.json()
    
    # Pin the dm
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response['message_id']})

    # Unpin the message given an invalid message id in dm
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': token1,
                                         'message_id': 0})
    
    assert unpin_response.status_code == InputError.code

# Test whether InputError raised if the message is already unpinned
def test_message_unpin_already(clear_data):
    
    # Register a user and save response
    register_response = register_user_1()
    token = register_response['token']

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Testing',
                                           'is_public': True})
    channel_response = channel_response.json()

    # Send a message in the channel
    send_response = requests.post(config.url + "message/send/v1",
                                  json={'token': register_response['token'],
                                        'channel_id': channel_response['channel_id'],
                                        'message': "Hallo"})
    send_response = send_response.json()
    
    # Pin the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token,
                        'message_id': send_response['message_id']})
    
    # Unpin the message
    requests.post(config.url + "message/unpin/v1",
                  json={'token': token,
                        'message_id': send_response['message_id']})
    
    # Unpin the same message again
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': token,
                                         'message_id': send_response['message_id']})

    assert unpin_response.status_code == InputError.code

# Test if accesserror is raised when message is unpinned by a non-owner in dm
def test_message_unpin_valid_but_not_owner_dm(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # User1 creates a dm with user2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_register_2]})
    dm_create_response = dm_create_response.json()

    # User2 sends a dm
    send_response = requests.post(config.url + "message/senddm/v1",
                                  json={'token': token2,
                                        'dm_id': dm_create_response['dm_id'],
                                        'message': "Let it go"})
    send_response = send_response.json()
    
    # User1 pins the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response['message_id']})
    
    # User2 attempts to unpin the message
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': token2,
                                         'message_id': send_response['message_id']})
    
    assert unpin_response.status_code == AccessError.code
    
# Test if accesserror is raised when message is unpinned by a non-owner in channel
def test_message_unpin_valid_but_not_owner_channel(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    
    # User1 creates a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'Tomorrow',
                                           'is_public': True})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']
    
    # User 2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})

    # User2 send a message in the channel
    send_response = requests.post(config.url + "message/send/v1",
                                  json={'token': token2,
                                        'channel_id': channel_id,
                                        'message': "Pure souls"})
    send_response = send_response.json()
    
    # User1 pins the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response['message_id']})
    
    # User2 attempts to unpin the message
    unpin_response = requests.post(config.url + "message/unpin/v1",
                                   json={'token': token2,
                                         'message_id': send_response['message_id']})

    assert unpin_response.status_code == AccessError.code

# Test if Inputerror is raised when user who hasnt joined any dm or channel 
# tries to unpin a message
def test_message_unpin_not_a_member(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = register_user_3()
    token3 = register_response3['token']
    
    # User1 creates a channel
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'LA',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})
    
    # User2 send a message in the channel
    send_channel_response = requests.post(config.url + "message/send/v1",
                                  json={'token': token2,
                                        'channel_id': channel_id,
                                        'message': "Glitter"})
    send_channel_response = send_channel_response.json()
    
    # User1 pins the channel message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_channel_response['message_id']})
    
    # User1 creates a dm with user2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_register_2]})
    dm_create_response = dm_create_response.json()

    # User2 sends a dm
    send_dm_response = requests.post(config.url + "message/senddm/v1",
                                  json={'token': token2,
                                        'dm_id': dm_create_response['dm_id'],
                                        'message': "KBBQ time"})
    send_dm_response = send_dm_response.json()
    
    # User1 pins the dm message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_dm_response['message_id']})
    
    # User3 attempts to unpin the channel message
    unpin_response1 = requests.post(config.url + "message/unpin/v1",
                                    json={'token': token3,
                                          'message_id': send_channel_response['message_id']})
    
    # User3 attempts to unpin the dm message
    unpin_response2 = requests.post(config.url + "message/unpin/v1",
                                    json={'token': token3,
                                          'message_id': send_dm_response['message_id']})
    
    assert unpin_response1.status_code == InputError.code
    assert unpin_response2.status_code == InputError.code

# Test if message can be unpinned if the member becomes an owner
def test_message_unpin_promoted_as_owner(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = register_user_3()
    token3 = register_response3['token']
    auth_user_id3 = register_response3['auth_user_id']
    
    # User 1 makes user 3 global owner
    requests.post(config.url + 'admin/userpermission/change/v1',
                  json={'token': token1,
                        'u_id': auth_user_id3,
                        'permission_id': 1})
    
    # User1 creates a channel
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Priv',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})
    
    # User2 sends a message in the channel
    send_response1 = requests.post(config.url + "message/send/v1",
                                  json={'token': token2,
                                        'channel_id': channel_id,
                                        'message': "Yeezy"})
    send_response1 = send_response1.json()

    # User2 sends a message in the channel
    send_response2 = requests.post(config.url + "message/send/v1",
                                  json={'token': token2,
                                        'channel_id': channel_id,
                                        'message': "Shoes"})
    send_response2 = send_response2.json()
    
    # User1 pins the first message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response1['message_id']})

    # User1 pins the second message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token1,
                        'message_id': send_response2['message_id']})
    
    # Add user2 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                  json = {'token': token1,
                          'channel_id': channel_id,
                          'u_id': auth_user_id2})
    
    # User3 attempts to unpin the message
    unpin_response1 = requests.post(config.url + "message/unpin/v1",
                                    json={'token': token3,
                                          'message_id': send_response1['message_id']})

    # User3 joins the channel
    requests.post(config.url + 'channel/join/v2',
                  json = {'token': token3,
                          'channel_id': channel_id})

    # User3 unpins the message as a global owner
    unpin_response3 = requests.post(config.url + "message/unpin/v1",
                                  json={'token': token3,
                                        'message_id': send_response1['message_id']})
    
    # User2 successfully unpins the message
    unpin_response2 = requests.post(config.url + "message/unpin/v1",
                                    json={'token': token2,
                                          'message_id': send_response2['message_id']})

    # user2 gets messages with start 0
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token2,
                                                     'channel_id': channel_id,
                                                     'start': 0})
    channel_messages_response = channel_messages_response.json()
    
    assert unpin_response1.status_code == InputError.code
    assert unpin_response2.status_code == 200
    assert unpin_response3.status_code == 200
    assert channel_messages_response['messages'][0]['is_pinned'] == False
