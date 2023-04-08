from datetime import datetime, timedelta
import time
import pytest
import requests 
from src import config
from .test_helpers import *

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test if user token is invalid
def test_message_send_later_invalid_token(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()


    # Create a channel with user 1
    channel_response = requests.post(config.url + 'channels/create/v2',
                json = {'token': register_response['token'],
                        'name': 'Validchannelone',
                        'is_public': True})
    channel_response = channel_response.json()

    # Test if the token given is invalid
    sendmessage = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": invalid_token1(),
                                          'channel_id': channel_response['channel_id'],
                                          'message': 'Hello There',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 403

# Test if Input error is raised if channel_id does not refer to a valid channel
def test_invalid_channel(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # User attempts to send a message in invalid channel
    sendmessage = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response['token'],
                                          'channel_id': 2000,
                                          'message': 'Hello There',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 400

# Test if the length of the message if over 1000 characters and raise an input error
def test_1000_characters_message(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': True})
    channel_response = channel_response.json()

    # User attempts to send a message that is 1000 characters long
    message_sendlater = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response['token'],
                                          'channel_id': channel_response['channel_id'],
                                          'message': '87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert message_sendlater.status_code == 400

# Raises an Acess error when the channel is valid but the user isn't a member of it
def test_not_channel_member(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # User 1 creates a channel
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': True})
    channel_response = channel_response.json()

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # User attempts to send a message in a channel they aren't a member of
    message_sendlater = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response2['token'],
                                          'channel_id': channel_response['channel_id'],
                                          'message': 'Hello There',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert message_sendlater.status_code == 403

# Test if an Input error is raised if the message is attempted to be sent in the past
def test_sending_message_in_the_past(clear_data):
   
    time_in_past = datetime.now() - timedelta(hours = 2)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': True})
    channel_response = channel_response.json()

    # User attempts to send a message in the past
    message_sendlater = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response['token'],
                                          'channel_id': channel_response['channel_id'],
                                          'message': 'Hello There',
                                          'time_sent': int(time.mktime(time_in_past.timetuple()))})
    
    # Status code is raised
    assert message_sendlater.status_code == 400

# Test message send later send correctly
def test_sendlater_correct_time(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 1)
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': True})
    channel_response = channel_response.json()

    # User attempts to send a message that is 1000 characters long
    message_sendlater = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response['token'],
                                          'channel_id': channel_response['channel_id'],
                                          'message': 'I just want to sleep',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    
    # Sleep for 2 seconds to allow the messages to be sent later
    time.sleep(2)

    # Get channel message info
    message_response = requests.get(config.url + "channel/messages/v2",
                                    params={
                                        'token': register_response['token'],
                                        'channel_id': channel_response['channel_id'],
                                        'start': 0
                                    })

    message_response = message_response.json()

    assert message_sendlater.status_code == 200

    assert message_response['messages'][0]['message_id'] == 1

    assert message_response['messages'][0]['u_id'] == 1

    assert message_response['messages'][0]['message'] == 'I just want to sleep'

# Test if the message has not been sent yet by adjusting the sleep timer to the incorrect time length
def test_sendlater_incorrect_time(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 2)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'Camel',
                                           'is_public': True})
    channel_response = channel_response.json()

    # User attempts to send a message that is 1000 characters long
    message_sendlater = requests.post(config.url + "message/sendlater/v1",
                                    json={"token": register_response['token'],
                                          'channel_id': channel_response['channel_id'],
                                          'message': 'I just want to sleep',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
   
    # Get channel message info
    message_response = requests.get(config.url + "channel/messages/v2",
                                    params={
                                        'token': register_response['token'],
                                        'channel_id': channel_response['channel_id'],
                                        'start': 0
                                    })

    message_response = message_response.json()

    assert message_sendlater.status_code == 200
    
    assert message_response['messages'] == []

# Check that if messages sent with sendlater and message_send in the same time
# frame do not have the same message_id
def test_message_sendlater_duplicate_message_ids(clear_data):

    # Register a user
    user = request_register("derrick@gmail.com", "password", "Derrick", "D")
    user = user.json()

    # Create a channel
    channel = request_channels_create(user['token'], "RANDCHANNEL", False)
    channel = channel.json()

    later_time = datetime.now() + timedelta(seconds = 2)
    later_time = int(time.mktime(later_time.timetuple()))

    # Set 2 messages to be sent in 2 seconds
    msg1 = request_message_sendlater(user['token'], channel['channel_id'], "hello", later_time)
    msg2 = request_message_sendlater(user['token'], channel['channel_id'], "hello", later_time)

    # Send a message with message/send/v1
    msg3 = request_message_send(user['token'], channel['channel_id'], "hello")

    msg1 = msg1.json()
    msg2 = msg2.json()
    msg3 = msg3.json()

    # Check that none of the message_ids are identical
    assert msg1['message_id'] != msg2['message_id'] != msg3['message_id']