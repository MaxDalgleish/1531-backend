import pytest
import requests
from src import config
from src.error import AccessError, InputError
from tests.test_helpers import create_user1, create_user2, create_user3, \
create_channel1, create_dm1, invalid_token4, send_message_in_channel_1, \
react_to_message, send_message_in_dm_1, thumbs_up_react_id, get_channel_messages, \
get_dm_messages, unreact_to_message, join_channel, leave_channel, leave_dm
from tests.test_helpers import request_user_stats, request_register, request_channels_create, \
                            request_dm_create, request_message_senddm, request_message_send, \
                        request_channel_invite, request_message_remove, invalid_token2, \
                        request_react, request_channel_join, request_dm_leave, request_channel_leave

@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Testing if the user token is invalid
def test_message_unreact_v1_token_invalid(clear):

    reg_response1 = request_register("derrick@gmail.com", "123456", "Derrick", "Doan")
    reg_response1 = reg_response1.json()

    channel_response1 = request_channels_create(reg_response1['token'], "Channel 1", True)
    channel_response1 = channel_response1.json()

    message_response1 = request_message_send(reg_response1['token'], channel_response1['channel_id'], "The first lecture will be on Wednesday 10am")
    message_response1 = message_response1.json()

    request_react(reg_response1['token'], message_response1['message_id'], 1)

    # Input invalid token into the function
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": invalid_token2(),
                                            "message_id": message_response1["message_id"],
                                            "react_id": 1}) 

    # Checking the Access Error code
    assert unreact_response.status_code == AccessError.code

# Testing if the message_id is not valid
def test_message_unreact_v1_message_id_invalid(clear):
    
    reg_response1 = create_user1()
    reg_response1 = reg_response1.json()

    channel_response1 = create_channel1(reg_response1)
    channel_response1 = channel_response1.json()

    message_response1 = send_message_in_channel_1(reg_response1, channel_response1)
    message_response1 = message_response1.json()

    react_to_message(reg_response1, message_response1, thumbs_up_react_id())

    # Input invalid message_id
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": reg_response1['token'],
                                            "message_id": message_response1["message_id"],
                                            "react_id": 12493}) 

    # Checking the Input Error code
    assert unreact_response.status_code == InputError.code

# Testing if the user is in the dm or not
def test_message_unreact_v1_dm_not_joined(clear):
    
    reg_response1 = request_register("Allan@gmail.com", "pwpwpwpw", "Allan", "Zhang")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("justins@gmail.com", "password", "Justin", "Son")
    reg_response2 = reg_response2.json()

    dm_response1 = request_dm_create(reg_response1['token'], [reg_response2["auth_user_id"]])
    dm_response1 = dm_response1.json()

    message_response1 = request_message_senddm(reg_response1['token'], dm_response1['dm_id'], "Bye")
    message_response1 = message_response1.json()

    request_react(reg_response2['token'], message_response1['message_id'], 1)

    # User 2 leaves the dm
    request_dm_leave(reg_response2['token'], dm_response1['dm_id'])

    # User 2 attemps to unreact the message
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": reg_response2['token'],
                                            "message_id": message_response1["message_id"],
                                            "react_id": 1}) 
    
    assert unreact_response.status_code == InputError.code

# Testing if the user is in the channel or not
def test_message_unreact_v1_channel_not_joined(clear):
     
    reg_response1 = request_register("Max@gmail.com", "pasword1", "Max", "Dalgeish")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("cynthia@gmail.com", "10101010101", "Cynthia", "Li")
    reg_response2 = reg_response2.json()

    channel_response1 = request_channels_create(reg_response1['token'], "CAMEL", True)
    channel_response1 = channel_response1.json()

    request_channel_join(reg_response2['token'], channel_response1['channel_id'])

    message_response1 = request_message_send(reg_response1['token'], channel_response1['channel_id'], "birb")
    message_response1 = message_response1.json()

    request_react(reg_response2['token'], message_response1['message_id'], 1)

    # User 2 leaves the channel
    request_channel_leave(reg_response2['token'], channel_response1['channel_id'])

    # User 2 attempts to unreact the message in the channel
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": reg_response2['token'],
                                            "message_id": message_response1["message_id"],
                                            "react_id": 1}) 

    # Checking the Input Error code
    assert unreact_response.status_code == InputError.code
    
# Testing if the react_id is invalid
def test_message_unreact_v1_react_id_invalid(clear):

    reg_response1 = request_register("Allan@gmail.com", "pwpwpwpw", "Allan", "Zhang")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("derrick@gmail.com", "123456", "Derrick", "Doan")
    reg_response2 = reg_response2.json()

    channel_response1 = request_channels_create(reg_response1['token'], "Channel 1", True)
    channel_response1 = channel_response1.json()

    request_channel_join(reg_response2['token'], channel_response1['channel_id'])

    message_response1 = request_message_send(reg_response1['token'], channel_response1['channel_id'], "Icecream")
    message_response1 = message_response1.json()

    request_react(reg_response2['token'], message_response1['message_id'], 1)

    # User 2 attempts to unreact the message with invalid react_id
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": reg_response2['token'],
                                            "message_id": message_response1["message_id"],
                                            "react_id": 99}) 

    # Checking for the InputError code
    assert unreact_response.status_code == InputError.code

# Testing correct unreacting in channel messages
def test_message_unreact_v1_channel_message(clear):
     
    reg_response1 = request_register("gyg@gmail.com", "quisedilla", "G", "YG")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("helloworld@gmail.com", "password", "hello", "world")
    reg_response2 = reg_response2.json()

    channel_response1 = request_channels_create(reg_response1['token'], "New channel", False)
    channel_response1 = channel_response1.json()

    request_channel_invite(reg_response1['token'], channel_response1['channel_id'], reg_response2['auth_user_id'])

    message_response1 = request_message_send(reg_response1['token'], channel_response1['channel_id'], "Icecream")
    message_response1 = message_response1.json()
    
    # Both users react to user 1's message
    request_react(reg_response1['token'], message_response1['message_id'], 1)
    request_react(reg_response2['token'], message_response1['message_id'], 1)

    # Both users unreact to the message in the channel
    requests.post(config.url + "message/unreact/v1",
                  json={"token": reg_response1['token'],
                        "message_id": message_response1["message_id"],
                        "react_id": 1}) 

    requests.post(config.url + "message/unreact/v1",
                  json={"token": reg_response2['token'],
                        "message_id": message_response1["message_id"],
                        "react_id": 1}) 

    # User 1 gets the channel messages data
    channel_messages_response1 = get_channel_messages(reg_response1['token'], message_response1['message_id'], 0)
    channel_messages_response1 = channel_messages_response1.json()

    assert channel_messages_response1['messages'][0]['reacts'] == [
                                            {   'react_id': 1,
                                                'u_ids': [],
                                                'is_this_user_reacted': False
                                            }
                                    ]

# Testing correct unreacting in DM messages
def test_message_unreact_v1_dm_message(clear):

    reg_response1 = request_register("hotmail@gmail.com", "543210987", "Calamari", "Ring")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("derrick@gmail.com", "00000000", "Derrick", "D")
    reg_response2 = reg_response2.json()

    dm_response1 = request_dm_create(reg_response1['token'], [reg_response2['auth_user_id']])
    dm_response1 = dm_response1.json()

    message_response1 = request_message_senddm(reg_response2['token'], dm_response1['dm_id'], "first message ever")
    message_response1 = message_response1.json()

    # Both users react to User 2's message
    request_react(reg_response1['token'], message_response1['message_id'], 1)
    request_react(reg_response2['token'], message_response1['message_id'], 1)

    # Both users unreact to the message in the channel
    requests.post(config.url + "message/unreact/v1",
                  json={ "token": reg_response1['token'],
                         "message_id": message_response1["message_id"],
                         "react_id": 1}) 

    requests.post(config.url + "message/unreact/v1",
                  json={ "token": reg_response2['token'],
                         "message_id": message_response1["message_id"],
                         "react_id": 1}) 

    # User 1 gets the dm message data
    dm_message_response1 = get_dm_messages(reg_response1['token'], dm_response1['dm_id'], 0)
    dm_message_response1 = dm_message_response1.json()
    
    assert dm_message_response1['messages'][0]['reacts'][0] == {'react_id': 1,
                                                                'u_ids': [],
                                                                'is_this_user_reacted': False
                                                                }
                                                            

# Testing when the message is not reacted by the user in the first place
def test_message_unreact_v1_reacted(clear):

    reg_response1 = request_register("hello@gmail.com", "password", "Calamari", "Ring")
    reg_response1 = reg_response1.json()

    reg_response2 = request_register("world@gmail.com", "12341234", "Basket", "Ball")
    reg_response2 = reg_response2.json()

    channel_response1 = request_channels_create(reg_response1['token'], "CAMEL", True)
    channel_response1 = channel_response1.json()

    request_channel_join(reg_response1['token'], channel_response1['channel_id'])

    message_response1 = request_message_send(reg_response1['token'], channel_response1['channel_id'], "hellohellohellohello")
    message_response1 = message_response1.json()

    # User 2 attempts to unreact the message without reacting first
    unreact_response = requests.post(config.url + "message/unreact/v1",
                                     json={ "token": reg_response2['token'],
                                            "message_id": message_response1["message_id"],
                                            "react_id": 1}) 

    # Checking the Input Error code
    assert unreact_response.status_code == InputError.code