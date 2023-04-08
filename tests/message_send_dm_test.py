import pytest
import requests
from src import config
import datetime
import time
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test whether AccessError status code is returned when calling message/senddm/v1
# with invalid token
def test_senddm_invalid_token(clear_data):
    
    # Register 2 users and save response
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response2 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    
    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # Create a dm and save response
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})
    
    dm_response = dm_response.json()
    
    # Call message/senddm with invalid token
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': invalid_token2(),
                                          'dm_id': dm_response['dm_id'],
                                          'message': "Hello world!"})
    
    assert senddm_response.status_code == 403

# Test whether InputError status code is returned when dm_id does not refer to 
# a valid dm
def test_senddm_invalid_dm_id(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'iloveunsw',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    
    register_response = register_response. json()

    # Call message/senddm/v1 with valid token and message but invalid dm_id
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': register_response['token'],
                                          'dm_id': 57839273,
                                          'message': "Hello world!"})

    assert senddm_response.status_code == 400

# Test whether AccessError status code is returned when dm_id is valid but 
# authorised user is not a member of the dm
def test_senddm_not_a_member(clear_data):
    
    # Register 2 users and save response
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'max@gmail.com',
                                             'password': 'helloworld',
                                             'name_first': 'Max', 
                                             'name_last': 'Dalgeish'})

    register_response2 =requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'allan@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Allan', 
                                            'name_last': 'Zhang'})                    

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # First user creates a dm with just themself
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': []})
    
    dm_response = dm_response.json()

    # Second user calls message/senddm/v1 but they are not a member
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': register_response2['token'],
                                          'dm_id': dm_response['dm_id'],
                                          'message': "Hello world!"})

    assert senddm_response.status_code == 403

# Test whether InputError status code is returned when message is empty
def test_senddm_empty_message(clear_data):
    
    # Register 2 users and save response
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response2 = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    
    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # Create a dm and save response
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})

    dm_response = dm_response.json()

    # First user calls message/senddm/v1 with empty string message
    send_response = requests.post(config.url + "message/senddm/v1",
                                  json={'token': register_response1['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': ""})
    
    assert send_response.status_code == 400

# Test whether InputError status code is returned when message is > 1000 characters
def test_senddm_message_too_long(clear_data):

    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response = register_response.json()

    # User creates a dm with just themself
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response['token'],
                                      'u_ids': []})
    
    dm_response = dm_response.json()

    # User calls message/senddm/v1 with a message > 1000 characters
    senddm_response = requests.post(config.url + "message/senddm/v1",
                                    json={'token': register_response['token'],
                                          'dm_id': dm_response['dm_id'],
                                          'message': "87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk"})

    assert senddm_response.status_code == 400

# Test whether each message has its own id even if other messages are in other
# channels or dms
def test_senddm_unique_message_id(clear_data):
    
    # Register 3 users and save response
    user1 = requests.post(config.url + "auth/register/v2", 
                          json={'email': 'derrick@gmail.com',
                                'password': 'password',
                                'name_first': 'Derrick', 
                                'name_last': 'Doan'})

    user2 = requests.post(config.url + "auth/register/v2", 
                          json={'email': 'hayden@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Hayden', 
                                'name_last': 'Smith'})
    
    user3 = requests.post(config.url + "auth/register/v2",
                          json={'email': "allan@gmail.com",
                                'password': "123456789",
                                'name_first': "Allan",
                                'name_last': "Zhang"})
    
    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a dm and response is saved
    dm_response1 = requests.post(config.url + "dm/create/v1",
                                 json={'token': user1['token'],
                                       'u_ids': []})
    
    dm_response1 = dm_response1.json()

    # User2 creates a channel and response is saved
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': user2['token'],
                                           'name': 'COMP1531',
                                           'is_public': False})

    channel_response = channel_response.json()

    # User3 creates another dm and response is saved
    dm_response2 = requests.post(config.url + "dm/create/v1",
                                 json={'token': user3['token'],
                                       'u_ids': [user1['auth_user_id'], 
                                                 user2['auth_user_id']]})
    
    dm_response2 = dm_response2.json()

    # User1 sends 2 messages in dm1
    message1 = requests.post(config.url + "message/senddm/v1",
                             json={'token': user1['token'],
                                   'dm_id': dm_response1['dm_id'],
                                   'message': "Hello world"})

    message2 = requests.post(config.url + "message/senddm/v1",
                             json={'token': user1['token'],
                                   'dm_id': dm_response1['dm_id'],
                                   'message': "world hello"})

    # User2 sends a message in channel
    message3 = requests.post(config.url + "message/send/v1",
                             json={'token': user2['token'],
                                   'channel_id': channel_response['channel_id'],
                                   'message': "Welcome 21T3 students"})

    # User3 sends 2 messages in dm2
    message4 = requests.post(config.url + "message/senddm/v1",
                             json={'token': user3['token'],
                                   'dm_id': dm_response2['dm_id'],
                                   'message': "Hello world"})

    message5 = requests.post(config.url + "message/senddm/v1",
                             json={'token': user3['token'],
                                   'dm_id': dm_response2['dm_id'],
                                   'message': "world hello"})

    
    # Check they all have unique message_ids
    assert message1.json() == {'message_id': 1}
    assert message2.json() == {'message_id': 2}
    assert message3.json() == {'message_id': 3}
    assert message4.json() == {'message_id': 4}
    assert message5.json() == {'message_id': 5}

# Test whether message is stored correctly using dm/messages/v1
def test_send_dm_message_saved_correctly(clear_data):
    
    # Register a user, save response
    user = requests.post(config.url + "auth/register/v2", 
									  json={'email': 'hayden@gmail.com',
									  		'password': 'helloworld',
									  		'name_first': 'Hayden', 
									  		'name_last': 'Smith'})

    user = user.json()

	# Create a channel and save response
    dm = requests.post(config.url + "dm/create/v1",
                       json={'token': user['token'],
                             'u_ids': []})
	
    dm = dm.json()

	# Send 2 messages on channel
    requests.post(config.url + "message/senddm/v1",
				  json={'token': user['token'],
						'dm_id': dm['dm_id'],
						'message': "Welcome to COMP1531"})

    # Get unix time stamp after message/senddm/v1 request was run
    message1_time = datetime.datetime.now()
    message1_time = int(time.mktime(message1_time.timetuple()))

    requests.post(config.url + "message/senddm/v1",
				  json={'token': user['token'],
						'dm_id': dm['dm_id'],
						'message': "The first lecture will be on Wednesday 10am"})

    # Get unix time stamp after message/senddm/v1 request was run
    message2_time = datetime.datetime.now()
    message2_time = int(time.mktime(message2_time.timetuple()))

	# Run channel/messages/v2 and save response
    messages_response = requests.get(config.url + "dm/messages/v1",
                                     params={'token': user['token'],
                                             'dm_id': dm['dm_id'],
                                             'start': 0})

    messages_response = messages_response.json()

    # check first message_is saved correctly (will be second in channel_messages list
    # as it is the second most recent message)
    assert messages_response['messages'][1]['message_id'] == 1
    assert messages_response['messages'][1]['u_id'] == user['auth_user_id']
    assert messages_response['messages'][1]['message'] == "Welcome to COMP1531"
    assert messages_response['messages'][1]['dm_id'] == dm['dm_id']
    
    # Check time_created is is within a second of the time the request was sent
    time_recorded1 = messages_response['messages'][1]['time_created']
    assert (message1_time - time_recorded1) < 2

    # check second message_is saved correctly (will be first in channel_messages list
    # as it is the most recent message)
    assert messages_response['messages'][0]['message_id'] == 2
    assert messages_response['messages'][0]['u_id'] == user['auth_user_id']
    assert messages_response['messages'][0]['message'] == "The first lecture will be on Wednesday 10am"
    assert messages_response['messages'][1]['dm_id'] == dm['dm_id']
    
    # Check time_created is is within a second of the time the request was sent
    time_recorded2 = messages_response['messages'][0]['time_created']
    assert (message2_time - time_recorded2) < 2




