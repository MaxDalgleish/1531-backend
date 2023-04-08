import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Registers user1 and returns register response
def register_user1():
    
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    
    return register_response1.json()

# Registers user2 and returns register response
def register_user2():
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                          json={'email': 'derrick@gmail.com',
                                'password': 'password',
                                'name_first': 'Derrick', 
                                'name_last': 'Doan'})
    
    return register_response2.json()

# Creates a channel and returns channel response
def create_channel1(creator):
    channel = requests.post(config.url + "channels/create/v2",
                            json={'token': creator['token'],
                                  'name': 'CatSociety',
                                  'is_public': True})

    return channel.json()

# Creates a dm and returns dm response
def create_dm1(creator, u_ids):
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': creator['token'],
                                      'u_ids': u_ids})
    
    return dm_response.json()

# Sends a message into dm and returns senddm response
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
                                          'message': "CSE servers are down"})
    
    return senddm_response.json()

# Sends a message in a channel and returns response
def send_message1(user, channel):
    send_response = requests.post(config.url + "message/send/v1",
                                   json={'token': user['token'],
                                    	 'channel_id': channel['channel_id'],
                                         'message': "Hello world"})
    
    return send_response.json()  

def send_message2(user, channel):
    send_response = requests.post(config.url + "message/send/v1",
                                   json={'token': user['token'],
                                    	 'channel_id': channel['channel_id'],
                                         'message': "CSE servers are down"})
    
    return send_response.json()  


# Tests whether AccessError status code is returned when token is invalid
def test_message_edit_token_invalid(clear_data):
    
    # register a user
    register_user1()

    # Call edit with an invalid_token
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json = {'token': invalid_token1(),
                                         'message_id': 8390,
                                         'message': 'Hello' })
    
    assert edit_response.status_code == 403


# Tests whether InputError status code is returned when message_id is non
# existent
def test_edit_message_id_invalid(clear_data):
    
    # Register a user and save response
    register_response = register_user1()

    # User calls edit with invalid message_id
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json = {'token': register_response['token'],
                                         'message_id': 8390,
                                         'message': 'Hello' })
    
    assert edit_response.status_code == 400

# Tests whether InputError status code is returned when message_id refers to 
# a valid message but user is not a member of the channel (ie the message does
# not refer to a valid message within a channel that the user is has joined)
def test_message_edit_not_a_channel_member(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 create a channel
    channel = create_channel1(user1)

    # User1 sends a message
    send_response = send_message1(user1, channel)

    # User 2 calls edit on the first message but they are not a member of the channel
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json = {'token': user2['token'],
                                         'message_id': send_response['message_id'],
                                         'message': "I don't like cats"})
    
    assert edit_response.status_code == 400

# Test whether AccessError status code is returned when message_id is valid
# but the channel member is not the user who sent the message and does not have
# owner permissions
def test_message_edit_channel_no_permissions(clear_data):
    
    # Register 2 users and save response
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a channel
    channel = create_channel1(user1)

    # User1 sends a message to the channel
    send_response = send_message1(user1, channel)

    # User2 joins channel
    requests.post(config.url + "channel/join/v2",
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id']})

    # User2 calls edit on user1's message but does not have owner permissions
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user2['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "NO!"})

    assert edit_response.status_code == 403

# Test whether a channel owner member can edit message
def test_channel_owner_can_edit_message(clear_data):
    
    # Register 2 users and save response
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a channel
    channel = create_channel1(user1)
    
    # User2 joins channel
    requests.post(config.url + "channel/join/v2",
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id']})

    # User2 sends 2 messages
    send_message1(user2, channel)
    send_response = send_message2(user2, channel)

    # User1 edits the second message and has owner permissions
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user1['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "Hello members"})

    assert edit_response.status_code == 200

# Check whether empty dictionary when user calls edit on their own message
def test_channel_message_edit_correct_return(clear_data):
    
    # Register a user and save response
    user = register_user1()

    # Create a channel and save response
    channel = create_channel1(user)

    # Send a valid message to the channel
    send_response = send_message1(user, channel)

    # User calls edit on their own message
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json = {'token': user['token'],
                                         'message_id': send_response['message_id'],
                                         'message': 'Welcome to COMP1531!' })
    
    assert edit_response.status_code == 200

# Tests whether InputError status code is returned when message is greater than 
# 1000 characters
def test_edit_channel_message_too_long(clear_data):
    
    # Register a user and save response
    user = register_user1()

    # Create a channel and save response
    channel = create_channel1(user)

    # Send a valid message
    send_response = send_message1(user, channel)
    
    # Call edit on the message but edited message is 1000+ chars
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk"})

    assert edit_response.status_code == 400

# Test whether calling edit with empty string deletes the message, test message 
# is deleted with channel/messages/v2
def test_edit_message_empty_str(clear_data):
    
    # Register a user and save response
    user = register_user1()

    # Create a channel and save response
    channel = create_channel1(user)

    # Send a valid message
    send_response = send_message1(user, channel)
    
    # Call edit on the message with empty string
    requests.put(config.url + "message/edit/v1",
                 json={'token': user['token'],
                       'message_id': send_response['message_id'],
                       'message': ""})

    # Check that the message was deleted using channel/messages/v2
    channel_messages = requests.get(config.url + "channel/messages/v2",
                                    params={'token': user['token'],
									 	    'channel_id': channel['channel_id'],
										    'start': 0})

    assert channel_messages.json() == {'messages': [],
                                     'start': 0,
                                     'end': -1}  

# Test whether a global owner who is a member of the channel can edit
def test_global_owner_can_edit_channel_message(clear_data):
    
    # Register 2 users, the first user will be a global member
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a channel
    channel = create_channel1(user2)

    # User2 invites user1 to channel
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id'],
                        'u_id': user1['auth_user_id']})

    # User2 sends a message in channel
    send_response = send_message1(user2, channel)

    # User1 calls edit on user2's message and they have global owner permissions
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user1['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "Nope"})

    assert edit_response.json() == {}

# Check whether edited message is saved correctly using channel/messages/v2
def test_channel_message_edit_saved_correctly(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a channel
    channel = create_channel1(user2)

    # User2 invites user1 to channel
    requests.post(config.url + 'channel/invite/v2',
                  json={'token': user2['token'],
                        'channel_id': channel['channel_id'],
                        'u_id': user1['auth_user_id']})

    # User2 sends a message in channel
    send_response = send_message1(user2, channel)

    # Call channel/messages/v2 to get old message info
    old_messages = requests.get(config.url + "channel/messages/v2",
                                params={'token': user2['token'],
                                        'channel_id': channel['channel_id'],
                                        'start': 0})

    old_messages = old_messages.json()

    # User1 calls edit on the first message
    requests.put(config.url + "message/edit/v1",
                 json={'token': user1['token'],
                       'message_id': send_response['message_id'],
                       'message': "Goodbye"})

    # Test that the edited message is saved correctly and nothing else in the 
    # message is changed using channel/message/v2
    new_messages = requests.get(config.url + "channel/messages/v2",
                                params={'token': user2['token'],
                                        'channel_id': channel['channel_id'],
                                        'start': 0})

    new_messages = new_messages.json()

    assert old_messages['messages'][0]['message_id'] == new_messages['messages'][0]['message_id']
    assert old_messages['messages'][0]['u_id'] == new_messages['messages'][0]['u_id']
    assert new_messages['messages'][0]['message'] == "Goodbye"
    assert old_messages['messages'][0]['time_created'] == new_messages['messages'][0]['time_created']

# Test whether InputError status code is returned when message_id is valid 
# but authorised user is not a member of the dm
def test_edit_message_dm_not_a_member(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a channel with just themself
    dm_create_response = create_dm1(user1, [])

    # User1 sends a valid message to the dm
    senddm_response = send_dm1(user1, dm_create_response)

    # User2 calls edit with valid message_id and message but they are not 
    # a member of the dm
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user2['token'],
                                       'message_id': senddm_response['message_id'],
                                       'message': "Can you invite me to this dm?"})

    assert edit_response.status_code == 400

# Test whether AccessError status code is returned when message_id is valid
# but the dm member is not the user who sent the message and does not have
# owner permissions
def test_edit_message_dm_no_permissions(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates a dm with user2
    dm_create_response = create_dm1(user1, [user2['auth_user_id']])

    # User1 sends a valid message to the dm
    senddm_response = send_dm1(user1, dm_create_response)

    # User2 calls edit with a valid message id and message but they do not have
    # owner permissions
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user2['token'],
                                       'message_id': senddm_response['message_id'],
                                       'message': "please remove me from this dm"})

    assert edit_response.status_code == 403

# Test whether dm creator can edit a message they did not send
def test_edit_message_dm_creator_can_edit(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a dm with user1
    dm_create_response = create_dm1(user2, [user1['auth_user_id']])

    # User1 sends 2 messages in dm
    send_dm1(user2, dm_create_response)
    senddm_response = send_dm2(user2, dm_create_response)

    # User1 calls edit with a valid message id and message and they are the dm
    # creator
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user1['token'],
                                       'message_id': senddm_response['message_id'],
                                       'message': "please remove me from this dm"})

    assert edit_response.status_code == 403

# Test whether InputError status code is returned when edited dm message is over 
# 1000 chars
def test_message_edit_dm_message_too_long(clear_data):

    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # Create a channel and save response
    dm = create_dm1(user1, [user2['auth_user_id']])

    # Send a valid message
    send_response = send_dm1(user2, dm)

    # Call edit on the message but edited message is 1000+ chars
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user2['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk"})

    assert edit_response.status_code == 400

# Test whether AccessError status code is returned when a global owner who is a
# member (but not the creator) of the dm tries to edit a message they did not send
def test_dm_global_owner_cant_edit(clear_data):
    
    # Register 2 users, the first user will be a global member
    user1 = register_user1()
    user2 = register_user2()

    # User2 creates a dm with user1
    dm_create_response = create_dm1(user2, [user1['auth_user_id']])

    # User2 sends a valid message to the dm
    senddm_response = send_dm1(user2, dm_create_response)

    # User1 calls edit on user2's message but they do not have owner permissions
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user1['token'],
                                       'message_id': senddm_response['message_id'],
                                       'message': "please remove me from this dm"})

    assert edit_response.status_code == 403

# Test whether empty dict is returned when user calls edit on their own message
# in a dm
def test_dm_message_edit_correct_return(clear_data):
    
    # Register a user
    user = register_user1()

    # User creates a dm with just themself
    dm_create_response = create_dm1(user, [])

    # User sends a valid message to the dm
    senddm_response = send_dm1(user, dm_create_response)

    # User calls edit on their own message
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user['token'],
                                       'message_id': senddm_response['message_id'],
                                       'message': "Goodbye"})

    assert edit_response.json() == {}

# check whether edited message is saved correctly using dm/messages/v1
def test_dm_message_edit_saved_correctly(clear_data):
    
    # Register 2 users
    user1 = register_user1()
    user2 = register_user2()

    # User1 creates dm with user2
    dm = create_dm1(user1, [user2['auth_user_id']])

    # User2 sends a message in dm
    send_response = send_dm1(user2, dm)

    # Call channel/messages/v2 to get old message info
    old_messages = requests.get(config.url + "dm/messages/v1",
                                params={'token': user2['token'],
                                        'dm_id': dm['dm_id'],
                                        'start': 0})

    old_messages = old_messages.json()

    # User2 calls edit on the first message
    requests.put(config.url + "message/edit/v1",
                 json={'token': user2['token'],
                       'message_id': send_response['message_id'],
                       'message': "Goodbye"})

    # Test that the edited message is saved correctly and nothing else in the 
    # message is changed using dm/message/v2
    new_messages = requests.get(config.url + "dm/messages/v1",
                                params={'token': user1['token'],
                                        'dm_id': dm['dm_id'],
                                        'start': 0})

    new_messages = new_messages.json()

    assert old_messages['messages'][0]['message_id'] == new_messages['messages'][0]['message_id']
    assert old_messages['messages'][0]['u_id'] == new_messages['messages'][0]['u_id']
    assert new_messages['messages'][0]['message'] == "Goodbye"
    assert old_messages['messages'][0]['time_created'] == new_messages['messages'][0]['time_created']
    assert old_messages['messages'][0]['dm_id'] == new_messages['messages'][0]['dm_id']

# Check whether empty edited message is deleted using dm/messages/v1
def test_dm_edit_message_empty_str(clear_data):
    
    # Register a user and save response
    user = register_user1()

    # Create a dm and save response
    dm = create_dm1(user, [])

    # Send a valid message
    send_response = send_dm1(user, dm)
    
    # Call edit on the message with empty string
    requests.put(config.url + "message/edit/v1",
                 json={'token': user['token'],
                       'message_id': send_response['message_id'],
                       'message': ""})

    # Check that the message was deleted using dm/messages/v2
    dm_messages = requests.get(config.url + "dm/messages/v1",
                                    params={'token': user['token'],
									 	  'dm_id': dm['dm_id'],
										  'start': 0})

    assert dm_messages.json() == {'messages': [],
                                  'start': 0,
                                  'end': -1}  

# Test that a removed dm message cannot be edited
def test_cant_edit_removed_dm_message(clear_data):
    
    # Register a user and save response
    user = register_user1()

    # Create a dm and save response
    dm = create_dm1(user, [])

    # Send a valid message
    send_response = send_dm1(user, dm)

    # Remove the dm message
    requests.delete(config.url + "message/remove/v1",
                    json={'token': user['token'],
                          'message_id': send_response['message_id']})

    # Try to edit the removed message, should raise InputError
    edit_response = requests.put(config.url + "message/edit/v1",
                                 json={'token': user['token'],
                                       'message_id': send_response['message_id'],
                                       'message': "Hello"})

    assert edit_response.status_code == 400

# Test removed channel message cannot be edited
def test_cant_edit_removed_channel_message(clear_data):
    
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

    # Try to edit the deleted message with its old message_id, should raise 
    # InputError
    edit_response1 = requests.put(config.url + "message/edit/v1",
                                 json={'token': user['token'],
                                       'message_id': message['message_id'],
                                       'message': "Hello"})

    # Try to edit message with message_id 0, should raise InputError
    edit_response2 = requests.put(config.url + "message/edit/v1",
                                 json={'token': user['token'],
                                       'message_id': 0,
                                       'message': "Hello"})

    assert edit_response1.status_code == 400
    assert edit_response2.status_code == 400
