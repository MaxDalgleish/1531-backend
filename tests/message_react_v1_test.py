import pytest
import requests
from src import config
from src.error import AccessError, InputError, Success
import tests.test_helpers as th

@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Testing if the user token is invalid
def test_message_react_v1_token_invalid(clear):

    reg_response1 = th.request_register("derrick@gmail.com", "123456", "Derrick", "Doan")
    reg_response1 = reg_response1.json()

    channel_response1 = th.request_channels_create(reg_response1['token'], "Channel 1", True)
    channel_response1 = channel_response1.json()

    message_response1 = th.request_message_send(reg_response1['token'], channel_response1['channel_id'], "The first lecture will be on Wednesday 10am")
    message_response1 = message_response1.json()

    # Input invalid token into the function
    react_response = requests.post(config.url + "message/react/v1",
                            json={"token": th.invalid_token4(),
                                  "message_id": message_response1["message_id"],
                                  "react_id": 1}) 

    # Checking the Access Error code
    assert react_response.status_code == AccessError.code
    
# Testing if the message_id is not valid
def test_message_react_v1_message_id_invalid(clear):
    
    reg_response1 = th.request_register("Allan@gmail.com", "pwpwpwpw", "Allan", "Zhang")
    reg_response1 = reg_response1.json()

    channel_response1 = th.request_channels_create(reg_response1['token'], "Channel 10000", False)
    channel_response1 = channel_response1.json()

    message_response1 = th.request_message_send(reg_response1['token'], channel_response1['channel_id'], "TYoyoyoyoyoyoyo")
    message_response1 = message_response1.json()

    # Input invalid message_id
    react_response = requests.post(config.url + "message/react/v1",
                            json={"token": reg_response1["token"],
                                  "message_id": 123456,
                                  "react_id": 1}) 

    # Checking for the Input Error code
    assert react_response.status_code == InputError.code

# Testing if the user has not joined the DM
def test_message_react_v1_dm_not_joined(clear):

    reg_response1 = th.request_register("justins@gmail.com", "password", "Justin", "Son")
    reg_response1 = reg_response1.json()

    reg_response2 = th.request_register("cynthia@gmail.com", "10101010101", "Cynthia", "Li")
    reg_response2 = reg_response2.json()

    reg_response3 = th.request_register("Max@gmail.com", "pasword1", "Max", "Dalgeish")
    reg_response3= reg_response3.json()

    dm_response1 = th.request_dm_create(reg_response1['token'], [reg_response2["auth_user_id"]])
    dm_response1 = dm_response1.json()

    message_response1 = th.request_message_senddm(reg_response1['token'], dm_response1['dm_id'], "BlahBlaBlah")
    message_response1 = message_response1.json()

    # Input user 3's token who is not in the dm
    react_response = requests.post(config.url + "message/react/v1",
                            json={"token": reg_response3["token"],
                                  "message_id": message_response1['message_id'],
                                  "react_id": 1}) 

    # Checking Input Error code
    assert react_response.status_code == InputError.code

# Testing if the user has not joined the channel
def test_message_react_v1_channel_not_joined(clear):

    reg_response1 = th.request_register("hello@gmail.com", "password", "Calamari", "Ring")
    reg_response1 = reg_response1.json()

    reg_response2 = th.request_register("world@gmail.com", "12341234", "Basket", "Ball")
    reg_response2 = reg_response2.json()

    channel_response1 = th.request_channels_create(reg_response1['token'], "CAMEL", True)
    channel_response1 = channel_response1.json()

    message_response1 = th.request_message_send(reg_response1['token'], channel_response1['channel_id'], "hellohellohellohello")
    message_response1 = message_response1.json()

    # Input user 2's token who is not in the channel
    react_response = requests.post(config.url + "message/react/v1",
                            json={"token": reg_response2["token"],
                                  "message_id": message_response1['message_id'],
                                  "react_id": 1}) 

    # Checking Input Error code
    assert react_response.status_code == InputError.code

# Testing if the react_id is invalid
def test_message_react_v1_react_id_invalid(clear):
     
    reg_response1 = th.request_register("hotmail@gmail.com", "543210987", "Calamari", "Ring")
    reg_response1 = reg_response1.json()

    reg_response2 = th.request_register("allan@gmail.com", "password", "allan", "Z")
    reg_response2 = reg_response2.json()

    reg_response3 = th.request_register("derrick@gmail.com", "00000000", "Derrick", "D")
    reg_response3 = reg_response3.json()

    dm_response1 = th.request_dm_create(reg_response1['token'], [reg_response2['auth_user_id'], reg_response3['auth_user_id']])
    dm_response1 = dm_response1.json()

    message_response1 = th.request_message_senddm(reg_response1['token'], dm_response1['dm_id'], "first message ever")
    message_response1 = message_response1.json()

    # Input invalid react id value
    react_response = requests.post(config.url + "message/react/v1",
                            json={"token": reg_response3["token"],
                                  "message_id": message_response1['message_id'],
                                  "react_id": 9389}) 

    # Checking Input Error code
    assert react_response.status_code == InputError.code

# Testing correct reacting in channel messages
def test_message_react_v1_channel_message_first_react(clear):

    reg_response1 = th.request_register("derrick@gmail.com", "999999999", "Derrick", "D")
    reg_response1 = reg_response1.json()

    channel_response1 = th.request_channels_create(reg_response1['token'], "COMP1531", True)
    channel_response1 = channel_response1.json()

    message_response1 = th.request_message_send(reg_response1['token'], channel_response1['channel_id'], "hey")
    message_response1 = message_response1.json()

    requests.post(config.url + "message/react/v1",
                  json={"token": reg_response1["token"],
                        "message_id": message_response1['message_id'],
                        "react_id": 1}) 

    channel_messages_response1 = th.get_channel_messages(reg_response1['token'], channel_response1['channel_id'], 0)
    channel_messages_response1 = channel_messages_response1.json()

    # Testing if the react is saved correctly
    assert channel_messages_response1['messages'][0]['reacts'] == [
                                                        {   'react_id': 1,
                                                            'u_ids': [reg_response1['auth_user_id']],
                                                            'is_this_user_reacted': True
                                                        }]

# Testing correct reacting in DM messages
def test_message_react_v1_dm_message_first_react(clear):
    
    reg_response1 = th.request_register("cynthia@gmail.com", ":)))))))", "Cynthia", "L")
    reg_response1 = reg_response1.json()

    reg_response2 = th.request_register("max@gmail.com", "12121212121", "Max", "d")
    reg_response2 = reg_response2.json()

    dm_response1 = th.request_dm_create(reg_response1['token'], [reg_response2['auth_user_id']])
    dm_response1 = dm_response1.json()

    message_response1 = th.request_message_senddm(reg_response1['token'], dm_response1['dm_id'], "hello")
    message_response1 = message_response1.json()

    requests.post(config.url + "message/react/v1",
                  json={"token": reg_response1["token"],
                        "message_id": message_response1['message_id'],
                        "react_id": 1}) 

    dm_message_response1 = th.get_dm_messages(reg_response1['token'], dm_response1['dm_id'], 0)
    dm_message_response1 = dm_message_response1.json()

    # Testing if the reacts is saved correctly
    assert dm_message_response1['messages'][0]['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [reg_response1['auth_user_id']],
            'is_this_user_reacted': True
        }
    ]

# Testing when the message is already reacted by the user
def test_message_react_v1_already_reacted(clear):

    reg_response1 = th.request_register("cynthia@gmail.com", "meepmeep", "Cynthia", "L")
    reg_response1 = reg_response1.json()

    channel_response1 = th.request_channels_create(reg_response1['token'], "Channel 5000", False)
    channel_response1 = channel_response1.json()

    message_response1 = th.request_message_send(reg_response1['token'], channel_response1['channel_id'], "Peppermint")
    message_response1 = message_response1.json()

    react_response1 = requests.post(config.url + "message/react/v1",
                                    json={"token": reg_response1["token"],
                                          "message_id": message_response1['message_id'],
                                          "react_id": 1}) 

    react_response2 = requests.post(config.url + "message/react/v1",
                                    json={"token": reg_response1["token"],
                                          "message_id": message_response1['message_id'],
                                          "react_id": 1}) 

    assert react_response1.status_code == Success.code
    assert react_response2.status_code == InputError.code

# Tests that a second react is saved correctly
def test_message_react_channel_second_react(clear):

    # Register 2 users
    user1 = th.request_register("abcd@gmail.com", "abcdefghi", "abc", "def")
    user2 = th.request_register("12345@gmail.com", "12345678", "numbers", "12345")

    user1 = user1.json()
    user2 = user2.json()

    th.request_channels_create(user2['token'], "Old channel", False)

    # User1 creates a new channel and invites user2
    channel = th.request_channels_create(user1['token'], "New channel", False)
    channel = channel.json()

    th.request_channel_invite(user1['token'], channel['channel_id'], user2['auth_user_id'])

    # Each user sends a message in the channel
    msg1 = th.request_message_send(user1['token'], channel['channel_id'], "Icecream")
    msg2 = th.request_message_send(user2['token'], channel['channel_id'], "is gross")

    msg1 = msg1.json()
    msg2 = msg2.json()

    # User1 2 reacts to message2, then user2 reacts to message2
    requests.post(config.url + "message/react/v1",
                  json={"token": user1["token"],
                        "message_id": msg2['message_id'],
                        "react_id": 1}) 

    requests.post(config.url + "message/react/v1",
                  json={"token": user2["token"],
                        "message_id": msg2['message_id'],
                        "react_id": 1}) 

    # User 2 reacts to msg1
    requests.post(config.url + "message/react/v1",
                  json={"token": user2["token"],
                        "message_id": msg1['message_id'],
                        "react_id": 1}) 

    # Get channel messages
    channel_messages = th.get_channel_messages(user1['token'], channel['channel_id'], 0)
    channel_messages = channel_messages.json()

    # Check that reacts is correct for msg2
    assert channel_messages['messages'][0]['reacts'] == [ 
                            {   'react_id': 1,
                                'u_ids': [user1['auth_user_id'], user2['auth_user_id']],
                                'is_this_user_reacted': True
                            }
                        ]
            
    # Check that reacts is correct for msg1
    assert channel_messages['messages'][1]['reacts'] == [ 
                            {   'react_id': 1,
                                'u_ids': [user2['auth_user_id']],
                                'is_this_user_reacted': False
                            }
                        ]

# Tests that a second react is saved correctly
def test_message_react_dm_second_react(clear):

    # Register 2 users
    user1 = th.request_register("gyg@gmail.com", "quisedilla", "G", "YG")
    user2 = th.request_register("helloworld@gmail.com", "password", "hello", "world")

    user1 = user1.json()
    user2 = user2.json()

    # Create dm1
    th.request_dm_create(user1['token'], [user2['auth_user_id']])

    # User2 creates dm2 with user1
    dm2 = th.request_dm_create(user2['token'], [user1['auth_user_id']])
    dm2 = dm2.json()

    # Both users send a message in dm2
    msg1 = th.request_message_senddm(user1['token'], dm2['dm_id'], "jk")
    msg2 = th.request_message_senddm(user2['token'], dm2['dm_id'], "icecream good")

    msg1 = msg1.json()
    msg2 = msg2.json()

    # User2 reacts to both dm messages
    requests.post(config.url + "message/react/v1",
                  json={"token": user2["token"],
                        "message_id": msg1['message_id'],
                        "react_id": 1}) 

    requests.post(config.url + "message/react/v1",
                  json={"token": user2["token"],
                        "message_id": msg2['message_id'],
                        "react_id": 1}) 

    # User1 reacts to msg2
    requests.post(config.url + "message/react/v1",
                  json={"token": user1["token"],
                        "message_id": msg2['message_id'],
                        "react_id": 1}) 

    # Get dm messages
    dm_messages = th.get_dm_messages(user1['token'], dm2['dm_id'], 0)
    dm_messages = dm_messages.json()

    # Check that msg1 reacts is correct
    assert dm_messages['messages'][1]['reacts'] == [ 
                                        {   'react_id': 1,
                                            'u_ids': [user2['auth_user_id']],
                                            'is_this_user_reacted': False
                                        }
                                    ]    

    # Check that msg2 reacts is correct
    assert dm_messages['messages'][0]['reacts'] == [ 
                                        {   'react_id': 1,
                                            'u_ids': [user2['auth_user_id'], user1['auth_user_id']],
                                            'is_this_user_reacted': True
                                        }
                                    ]

    

