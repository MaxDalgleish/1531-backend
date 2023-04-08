import pytest
import requests
from src import config
from tests.test_helpers import invalid_token3

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Register first user
def register_user1():
    
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    
    return register_response1.json()

# Register second user
def register_user2():
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                          json={'email': 'derrick@gmail.com',
                                'password': 'password',
                                'name_first': 'Derrick', 
                                'name_last': 'Doan'})
    
    return register_response2.json()

# Create first channel
def create_channel1(creator):
    channel = requests.post(config.url + "channels/create/v2",
                            json={'token': creator['token'],
                                  'name': 'CatSociety',
                                  'is_public': False})

    return channel.json()

# Create first dm
def create_dm1(creator, u_ids):
    
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': creator['token'],
                                      'u_ids': u_ids})
    
    return dm_response.json()

# Send a message in a dm
def send_dm1(user, dm):
    
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': user['token'],
                                          'dm_id': dm['dm_id'],
                                          'message': "Hello world!"})
    
    return senddm_response.json()

def send_dm2(user, dm):
    
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': user['token'],
                                          'dm_id': dm['dm_id'],
                                          'message': "It's raining today"})
    
    return senddm_response.json()

# Send a message in a channel
def send_message1(user, channel):
    
    send_response = requests.post(config.url + "message/send/v1",
                                   json={'token': user['token'],
                                    	 'channel_id': channel['channel_id'],
                                         'message': "Hello world"})
    
    return send_response.json() 

# Sends another message in the channel
def send_message2(user, channel):
    send_response = requests.post(config.url + "message/send/v1",
                                   json={'token': user['token'],
                                    	 'channel_id': channel['channel_id'],
                                         'message': "I like dogs"})
    
    return send_response.json() 

# Test if AccessError status code is returned for invalid token
def test_message_remove_invalid_token(clear_data):

    # Register a user
    user_response = register_user1()

    # Create a dm with just themself
    dm_response = create_dm1(user_response, [])

    # Send a message in the dm
    senddm_response = send_dm1(user_response, dm_response)

    # Call remove with invalid token but valid message_id
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': invalid_token3(),
                                            'message_id': senddm_response['message_id']})

    assert remove_response.status_code == 403

# Test is InputError status code is returned for non-existent message_id
def test_remove_non_existent_message_id(clear_data):
    
    # Register a user
    user_response = register_user1()

    # Call remove with valid token but non-existent message_id
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user_response['token'],
                                            'message_id': 39384})
    
    assert remove_response.status_code == 400

# Test if InputError status code is returned if message_id refers to a valid
# message in a channel but the user is not a member of the channel
def test_message_remove_channel_non_member(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a channel
    channel = create_channel1(user1)

    # User1 sends a message in the channel
    message = send_message1(user1, channel)

    # User2 calls delete but the message_id refers to a message in a channel
    # the user is not a part of
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user2['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 400

# Test if InputError status code is returned if message_id refers to a valid
# message in a dm but the user is not a member of the dm
def test_message_remove_dm_non_member(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a dm with just themself
    dm = create_dm1(user1, [])

    # User1 sends a message in their dm
    message = send_dm1(user1, dm)

    # User2 calls delete with a valid message_id but it refers to a message in 
    # a dm the user is not a part of
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user2['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 400

# Test if AccessError status code is returned if message_id refers to a valid
# message in a channel the user is a member of but they do not have permissions
# and are not the member who sent the message
def test_message_remove_channel_no_permissions(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a channel
    channel = create_channel1(user1)

    # User1 invites user2 to the channel
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': user1['token'],
                        'channel_id': channel['channel_id'],
                        'u_id': user2['auth_user_id']})

    # User1 sends a message in the channel
    message = send_message1(user1, channel)

    # User2 calls remove but they did not send the message and do not have
    # global owner status
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user2['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 403

# Test if AccessError status code is returned if message_id refers to a valid
# message in a dm the user is a member of but the user did not send the message
# and is not the owner
def test_message_remove_dm_no_permissions(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a dm with user2
    dm = create_dm1(user1, [user2['auth_user_id']])

    # User1 sends a message in their dm
    message = send_dm1(user1, dm)

    # User2 calls delete on the message but they did not send the message and
    # they are not the owner
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user2['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 403

# Test whether owner member can delete a message in their channel even though
# they did not send it
def test_message_channel_owner_can_remove(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a channel
    channel = create_channel1(user2)

    # User1 invites user2 to the channel
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id'],
                        'u_id': user1['auth_user_id']})

    # User1 sends a message in the channel
    message = send_message1(user1, channel)

    # User2 calls remove on a message they did not send and they are the dm
    # owner
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user2['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 200

# Test whether owner member can delete a message in their dm even though they
# did not send it
def test_message_dm_owner_can_remove(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a dm with user2
    dm = create_dm1(user1, [user2['auth_user_id']])

    # User2 sends 2 messages in the dm
    send_dm1(user2, dm)
    message2 = send_dm2(user2, dm)

    # User2 calls remove on a message they did not send but they are the dm
    # creator
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user1['token'],
                                            'message_id': message2['message_id']})
    
    assert remove_response.status_code == 200

# Test whether global owner who is a member of a channel (but not the channel 
# owner) can delete a message they did not send
def test_channel_message_global_owner_can_remove(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a channel
    channel = create_channel1(user2)

    # User2 invites user1 to the channel
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id'],
                        'u_id': user1['auth_user_id']})

    # User2 sends a message in the channel
    message1 = send_message1(user2, channel)

    # User2 sends another message
    send_message2(user2, channel)

    # User1 calls remove on message2, they did not send this message but they
    # are a global owner
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user1['token'],
                                            'message_id': message1['message_id']})
    
    assert remove_response.status_code == 200

# Test whether AcessError status code is returned if a global owner who is not
# the dm creator calls remove on a message they did not send
def test_dm_message_global_owner_cant_remove(clear_data):
    
    # Register 2 users, User1 will have global owner permissions
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a dm with user1
    dm = create_dm1(user2, [user1['auth_user_id']])

    # User2 sends a message in their dm
    message = send_dm1(user2, dm)

    # User1 calls delete on a message they did not send and they are a 
    # global owner
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user1['token'],
                                            'message_id': message['message_id']})
    
    assert remove_response.status_code == 403

# Test that the message is removed from channel['messages] using 
# channel/messages/v2
def test_channel_message_remove(clear_data):

    # Register a user
    user = register_user1()

    # Create a channel
    channel = create_channel1(user)

    # Send a message in channel
    message = send_message1(user, channel)

    # Call delete on the message
    requests.delete(config.url + "message/remove/v1",
                    json={'token': user['token'],
                          'message_id': message['message_id']})

    # Call channel_messages and check that the message has been deleted
    channel_messages = requests.get(config.url + "channel/messages/v2",
                                    params={'token': user['token'],
                                            'channel_id': channel['channel_id'],
                                            'start': 0})

    assert channel_messages.json() == {'messages': [],
                                     'start': 0,
                                     'end': -1}  

# Test that an InputError status code is returned when a user calls remove on
# a removed channel message
def test_message_remove_on_removed_message(clear_data):
    
    # Register a user
    user = register_user1()

    # Create a channel
    channel = create_channel1(user)

    # Send a message in channel
    message1 = send_message1(user, channel)

    # Call delete on the message
    requests.delete(config.url + "message/remove/v1",
                    json={'token': user['token'],
                          'message_id': message1['message_id']})

    # Call delete on the deleted message
    remove_response = requests.delete(config.url + "message/remove/v1",
                                      json={'token': user['token'],
                                            'message_id': message1['message_id']})
    
    assert remove_response.status_code == 400

# Test that the message is removed from dm['messages'] using 
# dm/messages/v1
def test_message_removed_from_dm(clear_data):
    
    # Register a user
    user = register_user1()

    # Create a dm with just themself
    dm = create_dm1(user, [])

    # User2 sends a message in their dm
    message = send_dm1(user, dm)

    # Remove the dm
    requests.delete(config.url + "message/remove/v1",
                                      json={'token': user['token'],
                                            'message_id': message['message_id']})

    # Call dm/messages/v1 and test that the dm message is removed
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': user['token'],
                                               'dm_id': dm['dm_id'],
                                               'start': 0})

    dm_message_response = dm_message_response.json()
    assert dm_message_response['messages'] == []

# Test that a removed message cannot be removed again
def test_dm_message_remove_cannot_be_removed_twice(clear_data):

    # Register a user
    user = register_user1()

    # Create a dm with just themself
    dm = create_dm1(user, [])

    # User2 sends a message in their dm
    message = send_dm1(user, dm)

    # Remove the dm
    requests.delete(config.url + "message/remove/v1",
                    json={'token': user['token'],
                          'message_id': message['message_id']})

    second_remove = requests.delete(config.url + "message/remove/v1",
                                    json={'token': user['token'],
                                          'message_id': message['message_id']})

    assert second_remove.status_code == 400
