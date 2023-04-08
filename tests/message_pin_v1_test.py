import pytest
import requests
from src import config
from src.error import AccessError, InputError
from .test_helpers import *

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test if invalid token raises an AccessError
def test_message_pin_invalid_token(clear_data):

    # Register user 1
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = request_dm_create(token1, 
                                           [])
    dm_create_response = dm_create_response.json()
    
    # Send a dm
    send_response = request_message_senddm(token1,
                                           dm_create_response['dm_id'],
                                           "Just do it")
    send_response = send_response.json()
    
    # Pin the dm message given an invalid token
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': invalid_token1(),
                                       'message_id': send_response['message_id']})

    assert pin_response.status_code == AccessError.code
    
# Test whether InputError is raised given invalid message id for channel
def test_message_pin_channel_invalid_id(clear_data):
    
    # Register a user and save response
    register_response = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response = register_response.json()
    token = register_response['token']

    # Create a channel and save response
    channel_response = request_channels_create(register_response['token'],
                                               'Vroom',
                                               False)
    channel_response = channel_response.json()

    # Send a message in the channel
    request_message_send(register_response['token'],
                         channel_response['channel_id'],
                         "Skrt Skrt")
    
    # Pin the message given an invalid message id in channel
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': token,
                                       'message_id': 0})

    assert pin_response.status_code == InputError.code

# Test whether InputError is raised given invalid message id for dm
def test_message_pin_dm_invalid_id(clear_data):

    # Register user 1
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = request_dm_create(token1,
                                           [])
    dm_create_response = dm_create_response.json()
    
    # Send a dm
    request_message_senddm(token1,
                           dm_create_response['dm_id'],
                           "Aloha :)")

    # Pin the message given an invalid message id in dm
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': token1,
                                       'message_id': 0})
    
    assert pin_response.status_code == InputError.code

# Test whether InputError raised if the message is already pinned
def test_message_pin_already(clear_data):
    
    # Register a user and save response
    register_response = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response = register_response.json()
    token = register_response['token']

    # Create a channel and save response
    channel_response = request_channels_create(register_response['token'],
                                               'bobaicecream',
                                               False)
    channel_response = channel_response.json()

    # Send a message in the channel
    send_response = request_message_send(register_response['token'],
                                         channel_response['channel_id'],
                                         "yummy")
    send_response = send_response.json()
    
    # Pin the message
    requests.post(config.url + "message/pin/v1",
                  json={'token': token,
                        'message_id': send_response['message_id']})
    
    # Pin the same message again
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': token,
                                       'message_id': send_response['message_id']})

    assert pin_response.status_code == InputError.code

# Test if accesserror is raised when message is pinned by a non-owner in dm
def test_message_pin_valid_but_not_owner_dm(clear_data):
    
    # Register user1 and save response
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = request_register('cynthia@gmail.com',
                                         'password123456',
                                         'Cynthia', 
                                         'Li')
    register_response2 = register_response2.json()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # User1 creates a dm with user2
    dm_create_response = request_dm_create(token1,
                                           [auth_register_2])
    dm_create_response = dm_create_response.json()

    # User2 sends a dm message
    send_response = request_message_senddm(token2,
                                           dm_create_response['dm_id'],
                                           "Lets go")
    send_response = send_response.json()
    
    # User2 attempts to pin the message
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': token2,
                                       'message_id': send_response['message_id']})
    
    assert pin_response.status_code == AccessError.code
    
# Test if accesserror is raised when message is pinned by a non-owner in channel
def test_message_pin_valid_but_not_owner_channel(clear_data):
    
    # Register user1 and save response
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = request_register('cynthia@gmail.com',
                                         'password123456',
                                         'Cynthia', 
                                         'Li')
    register_response2 = register_response2.json()
    token2 = register_response2['token']
    
    # User1 creates a channel and save response
    channel_response = request_channels_create(token1,
                                               'Yesterday',
                                               True)
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']
    
    # User 2 joins channel
    request_channel_join(token2,
                         channel_id)

    # User2 send a message in the channel
    send_response = request_message_send(token2,
                                         channel_id,
                                         "Off the grid")
    send_response = send_response.json()
    
    # User2 attempts to pin the message
    pin_response = requests.post(config.url + "message/pin/v1",
                                 json={'token': token2,
                                       'message_id': send_response['message_id']})

    assert pin_response.status_code == AccessError.code

# Test if inputerror is raised when user who hasnt joined any dm or channel 
# tries to pin a message
def test_message_pin_not_a_member(clear_data):
    
    # Register user1 and save response
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = request_register('cynthia@gmail.com',
                                         'password123456',
                                         'Cynthia', 
                                         'Li')
    register_response2 = register_response2.json()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = request_register('Derrick@gmail.com',
                                         'password000',
                                         'Derrick',
                                         'Doan')
    register_response3 = register_response3.json()
    token3 = register_response3['token']
    
    # User1 creates a channel
    channel_create_response = request_channels_create(token1,
                                                      'Downtown',
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    request_channel_join(token2,
                         channel_id)
    
    # User2 send a message in the channel
    send_channel_response = request_message_send(token2,
                                                 channel_id,
                                                 "Wednesday")
    send_channel_response = send_channel_response.json()
    
    # User1 creates a dm with user2
    dm_create_response = request_dm_create(token1,
                                           [auth_register_2])
    dm_create_response = dm_create_response.json()

    # User2 sends a dm
    send_dm_response = request_message_senddm(token2,
                                              dm_create_response['dm_id'],
                                              "KBBQ time")
    send_dm_response = send_dm_response.json()
    
    # User3 attempts to pin the channel message
    pin_response1 = requests.post(config.url + "message/pin/v1",
                                  json={'token': token3,
                                        'message_id': send_channel_response['message_id']})
    
    # User3 attempts to pin the dm message
    pin_response2 = requests.post(config.url + "message/pin/v1",
                                  json={'token': token3,
                                        'message_id': send_dm_response['message_id']})
    
    assert pin_response1.status_code == InputError.code
    assert pin_response2.status_code == InputError.code

# Test if message can be pinned if the member becomes an owner
def test_message_pin_promoted_as_owner(clear_data):
    
    # Register user1 and save response
    register_response1 = request_register('justin@gmail.com',
                                         'password123',
                                         'Justin',
                                         'Son')
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = request_register('cynthia@gmail.com',
                                         'password123456',
                                         'Cynthia', 
                                         'Li')
    register_response2 = register_response2.json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = request_register('Derrick@gmail.com',
                                         'password000',
                                         'Derrick',
                                         'Doan')
    register_response3 = register_response3.json()
    token3 = register_response3['token']
    auth_user_id3 = register_response3['auth_user_id']
    
    # User 1 makes user 3 global owner
    requests.post(config.url + 'admin/userpermission/change/v1',
                  json={'token': token1,
                        'u_id': auth_user_id3,
                        'permission_id': 1})
    
    # User1 creates a channel
    channel_create_response = request_channels_create(token1,
                                                      'Priv',
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    request_channel_join(token2,
                         channel_id)
    
    # User2 sends a message in the channel
    send_response1 = request_message_send(token2,
                                          channel_id,
                                          "Yeezy")
    send_response1 = send_response1.json()

    # User2 sends a message in the channel
    send_response2 = request_message_send(token2,
                                          channel_id,
                                          "Shoes")
    send_response2 = send_response2.json()
    
    # User1 adds user2 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                  json = {'token': token1,
                          'channel_id': channel_id,
                          'u_id': auth_user_id2})
    
    # User3 attempts pins the message
    pin_response1 = requests.post(config.url + "message/pin/v1",
                                  json={'token': token3,
                                        'message_id': send_response1['message_id']})

    # User3 joins the channel
    request_channel_join(token3,
                         channel_id)

    # User3 pins the message as a global owner
    pin_response3 = requests.post(config.url + "message/pin/v1",
                                  json={'token': token3,
                                        'message_id': send_response1['message_id']})

    # User2 attempts to pin the message
    pin_response2 = requests.post(config.url + "message/pin/v1",
                                  json={'token': token2,
                                        'message_id': send_response2['message_id']})
    
    # user2 gets messages with start 0
    channel_messages_response = get_channel_messages(token2,
                                                     channel_id,
                                                     0)
    channel_messages_response = channel_messages_response.json()

    assert pin_response1.status_code == InputError.code
    assert pin_response2.status_code == 200
    assert pin_response3.status_code == 200
    assert channel_messages_response['messages'][0]['is_pinned'] == True