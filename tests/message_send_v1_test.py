import pytest
import requests
from src import config
from tests.test_helpers import invalid_token4
import datetime
import time

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test whether AcessError status code is returned on invalid token
def test_message_send_invalid_token(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': False})

    channel_response = channel_response.json()

    # Get response on message/send/v1 with valid channel and message but invalid token
    send_response = requests.post(config.url + "message/send/v1",
                                 json={'token': invalid_token4(),
                                       'channel_id': channel_response['channel_id'],
                                       'message': "Hello"})

    assert send_response.status_code == 403

# Test whether InputError status code is returned on invalid channel_id
def test_message_send_invalid_channel(clear_data):
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    
    register_response = register_response.json()

    # Get response on message/send/v1 with valid token and message but invalid 
    # channel_id
    send_response = requests.post(config.url + "message/send/v1",
                                 json={'token': register_response['token'],
                                       'channel_id': 8290,
                                       'message': "Hi, nice to meet you!"})

    # Check InputError status code is returned
    assert send_response.status_code == 400

# Test whether InputError status code is returned on empty message
def test_message_send_empty_message(clear_data):
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'iloveunsw',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    
    register_response = register_response. json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'CatSociety',
                                           'is_public': False})
    
    channel_response = channel_response.json()

    # Get response on message/send/v1 with valid token and channel_id but empty message
    send_response = requests.post(config.url + "message/send/v1",
                                 json={'token': register_response['token'],
                                       'channel_id': channel_response['channel_id'],
                                       'message': ""})

    # Check InputError status code is returned
    assert send_response.status_code == 400

# Test whether InputError status code is returned when message length is over
# 1000 characters
def test_message_send_message_too_long(clear_data):
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': False})

    channel_response = channel_response.json()

    # Get response on message/send/v1 with valid token and channel_id but 1002 char message
    send_response = requests.post(config.url + "message/send/v1",
                                 json={'token': register_response['token'],
                                       'channel_id': channel_response['channel_id'],
                                       'message': "87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk"})

    # Check InputError status code is returned
    assert send_response.status_code == 400

# Test whether AccessError status code is returned when channel_id is valid but
# auth_user is not a member of the channel
def test_message_send_not_a_member(clear_data):
    # Register 2 users
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

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response1['token'],
                                           'name': 'COMP1531',
                                           'is_public': False})

    channel_response = channel_response.json()

    # Get response on message/send/v1 on valid channel_id, valid message but
    # user is not a member
    send_response = requests.post(config.url + "message/send/v1",
                                  json={'token': register_response2['token'],
                                    	'channel_id': channel_response['channel_id'],
                                        'message': "hello world"})

    # Check that AccessError status code is returned
    assert send_response.status_code == 403  

# Test whether correct message_id is returned even when messages are sent from 
# different channels
def test_correct_message_id_return(clear_data):
	# Register a user, save response
    register_response = requests.post(config.url + "auth/register/v2", 
									  json={'email': 'max@gmail.com',
									        'password': 'helloworld',
									        'name_first': 'Max', 
									        'name_last': 'Dalgeish'})

    register_response = register_response.json()

	# Create a channel and save response
    channel_response1 = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'COMP1531',
                                           'is_public': False})

    channel_response1 = channel_response1.json()  

	# Create another channel and save response
    channel_response2 = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'W15A_CAMEL',
                                           'is_public': False})
	
    channel_response2 = channel_response2.json()

	# Send 2 messages on channel 1 and save response
    message_response1 = requests.post(config.url + "message/send/v1",
                                  	  json={'token': register_response['token'],
                                    		'channel_id': channel_response1['channel_id'],
                                        	'message': "Welcome to COMP1531"})

    message_response1 = message_response1.json()

    message_response2 = requests.post(config.url + "message/send/v1",
                                  	  json={'token': register_response['token'],
                                    		'channel_id': channel_response1['channel_id'],
                                        	'message': "The first lecture will be on Wednesday 10am"})

    message_response2 = message_response2.json()

	# Send 2 messages on channel 2 and save response
    message_response3 = requests.post(config.url + "message/send/v1",
                                  	  json={'token': register_response['token'],
                                    		'channel_id': channel_response2['channel_id'],
                                        	'message': "Hi team, nice to meet you all!"})

    message_response3 = message_response3.json()

    message_response4 = requests.post(config.url + "message/send/v1",
                                  	  json={'token': register_response['token'],
                                    		'channel_id': channel_response2['channel_id'],
                                        	'message': "Let's hold our first meeting during Wednesday's lab!"})
    message_response4 = message_response4.json()

    assert message_response1 == {'message_id': 1}
    assert message_response2 == {'message_id': 2}
    assert message_response3 == {'message_id': 3}
    assert message_response4 == {'message_id': 4}

# Check messages are saved correctly to data_store (using channel_messages)
def test_message_send_saved_correctly(clear_data):
	
    # Register a user, save response
    register_response = requests.post(config.url + "auth/register/v2", 
									  json={'email': 'hayden@gmail.com',
									  		'password': 'helloworld',
									  		'name_first': 'Hayden', 
									  		'name_last': 'Smith'})

    register_response = register_response.json()

	# Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'COMP1531',
                                           'is_public': False})
	
    channel_response = channel_response.json()

	# Send 2 messages on channel
    requests.post(config.url + "message/send/v1",
				  json={'token': register_response['token'],
						'channel_id': channel_response['channel_id'],
						'message': "Welcome to COMP1531"})

    time_message1 = datetime.datetime.now()
    time_message1 = int(time.mktime(time_message1.timetuple()))

    requests.post(config.url + "message/send/v1",
				  json={'token': register_response['token'],
						'channel_id': channel_response['channel_id'],
						'message': "The first lecture will be on Wednesday 10am"})

    time_message2 = datetime.datetime.now()
    time_message2 = int(time.mktime(time_message2.timetuple()))

	# Run channel/messages/v2 and save response
    messages_response = requests.get(config.url + "channel/messages/v2",
                                     params={'token': register_response['token'],
                                             'channel_id': channel_response['channel_id'],
                                             'start': 0})

    messages_response = messages_response.json()

    # check first message_is saved correctly (will be second in channel_messages list
    # as it is the second most recent message)
    assert messages_response['messages'][1]['message_id'] == 1
    assert messages_response['messages'][1]['u_id'] == register_response['auth_user_id']
    assert messages_response['messages'][1]['message'] == "Welcome to COMP1531"
    assert messages_response['messages'][1]['channel_id'] == channel_response['channel_id']
    
    # Check time_created is is within a second of the time the request was sent
    time_recorded1 = messages_response['messages'][1]['time_created']
    assert (time_message1 - time_recorded1) < 2

    # check second message_is saved correctly (will be first in channel_messages list
    # as it is the most recent message)
    assert messages_response['messages'][0]['message_id'] == 2
    assert messages_response['messages'][0]['u_id'] == register_response['auth_user_id']
    assert messages_response['messages'][0]['message'] == "The first lecture will be on Wednesday 10am"
    assert messages_response['messages'][0]['channel_id'] == channel_response['channel_id']
    
    # Check time_created is is within a second of the time the request was sent
    time_recorded2 = messages_response['messages'][0]['time_created']
    assert (time_message2 - time_recorded2) < 2




