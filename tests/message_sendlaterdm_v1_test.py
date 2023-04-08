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
def test_message_sendlater_dm_invalid_token(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()


    # Create a dm with user 1
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': []})
    dm_response = dm_response.json()

    # send message with an invalid token
    sendmessage = requests.post(config.url + "message/sendlaterdm/v1",
                                    json={"token": invalid_token1(),
                                          'dm_id': dm_response['dm_id'],
                                          'message': 'Hello There',
                                          'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 403

# Test if input error is raised if dm_id doesn't refer to a valid dm
def test_invalid_dm_id(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()


    # Attempt to send a message to the dm that doesn't exist
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response['token'],
                                        'dm_id': 5000,
                                        'message': 'Hello There',
                                        'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 400

# Test if the length of the message is over 1000 characters and an input error is raised
def test_message_length_1000(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()


    # Create a dm with user 1
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': []})
    dm_response = dm_response.json()

    # Attempt to send a message that is over 1000 characters
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': '87Hon45kXI9hY8fgZ2QaWDRpiAXwfrkSnsdiTEzyf5lDrl8FFgl2yJn2N6OxbBMxXrfgcYMpuzBMkY6hnPkw1iIYlGFGqrsGgrUvON7D59CmAL7W4JWz4TWm8brwt0neKwapugRtfiPgo61MGK7pt5ruSoDSn3VdWDlp7j2JPc5HbhN4fl9E7PTMVzBj4oDDAkBtvpXLLzvUje1rf19NHOAnMDFetQV07fbSm1wYYIczTa2BWw6JldiMwj4Ss0N2JdrdckzEIWv3ZxofZhLJDAaiasMm9kP5m28eLdnKLMCg4XPP9rDSaKHQMPPdf0oNAp1CHWRVEHkF8P4J7zcJOxPepcJ7HI43vobuJYQwP4DG0t9ugco8r5E5QkyBCweU5qLg7gJDrpTohuEvszAvTtRAyFGBy04BVK3PZsUnK5GfILjxtxPZBZwEdmTtAd7tyoTS7ow7KjVT6aSqESMmFcaMtaK0Fr1csaHDVEKBvssEkkKkUOsT9YaS3CWSwVUVXZuEELB6tvkhBzmvjF4uYotxVaiVhFE5lR2SyNHMBuwP3sM6sPtMVWlQQNep3kL3OSi5l7CTRR8Ipcn2jtNbu260YAZ2SAw9YJdb0xzu9B02cYmPbfhzi87gYNe0DAocrmPo8WMLQheZLrbqRhSnxkGU3a1Xf8fZBW80T5RJvZHl0ZaxbKOsBeAK890gUgVtponFFSSB1Pmm4rlUB1hT9ghF6yGv5g5wjFGocN0CcPZuAzss1dKWh5NNEthB9kvzRM8nZMBClde9nJtY3k01ud63Sl7dZ23u7B0x8gFbXzefnStXIgNeUmFfsDqn5Z8bIXFS8qHJYrsg8PnE6ALV52YnEPtdomYo43z4S97j29OFAdkohFJI0oFaOAnuWjsax2zAq4QDYauQu7EqlwUwJMZ0ppbZ15eL9eLZpDnIMoWL3hqq2nbVxrE2ZQIc3N2Gfzr3mttAtpiukISX4GfrJXMsOQFNOaGy6bmRD447Rk',
                                        'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 400

# Test if an Access Error is raised when the dm_id is valid but the member is not a dm member
def test_not_dm_member(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 3)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create a dm with only user 1
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': []})
    dm_response = dm_response.json()

    # User 2 attempts to send a message in the dm but they aren't a member of the dm
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response2['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': 'Hello There',
                                        'time_sent': int(time.mktime(time_in_future.timetuple()))})
    assert sendmessage.status_code == 403

# Test if the time_sent is in the past and an Input Error is raised
def test_time_sent_in_past(clear_data):
    
    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Create a dm with user 1
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': []})
    dm_response = dm_response.json()

    # Setting the time in the past for 2 hours earlier
    time_in_past = datetime.now() - timedelta(hours = 2)

    # Attempt to send a message in the dm in the past
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': 'Hello There',
                                        'time_sent': int(time.mktime(time_in_past.timetuple()))})

    assert sendmessage.status_code == 400
    
# Test if the message has been sent correctly by adjusting the sleep timer to the correct time length
def test_sendlaterdm_correct_time(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 1)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create a dm between user 1 and user 2
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': [register_response2["auth_user_id"]]})
    dm_response = dm_response.json()

    # User 2 calls message/sendlaterdm
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response2['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': 'Hello There',
                                        'time_sent': int(time.mktime(time_in_future.timetuple()))})
    
    # Sleep for 2 seconds to allow the messages to be sent later
    time.sleep(2)

    # Get dm message info
    message_response = requests.get(config.url + "dm/messages/v1",
                                    params={
                                        'token': register_response2['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'start': 0
                                    })

    message_response = message_response.json()

    assert sendmessage.status_code == 200

    assert message_response['messages'][0]['message_id'] == 1

    assert message_response['messages'][0]['u_id'] == 2

    assert message_response['messages'][0]['message'] == 'Hello There'

# Test if the message has not been sent yet by adjusting the sleep timer to the incorrect time length
def test_sendlaterdm_incorrect_time(clear_data):
    
    time_in_future = datetime.now() + timedelta(seconds = 1)

    # Register user 1
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create a dm between user 1 and user 2
    dm_response = requests.post(config.url + 'dm/create/v1',
                                json = {'token': register_response['token'],
                                        'u_ids': [register_response2["auth_user_id"]]})
    dm_response = dm_response.json()

    # User 2 attempts to send a message in the dm but they aren't a member of the dm
    sendmessage = requests.post(config.url + 'message/sendlaterdm/v1',
                                json = {'token': register_response2['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'message': 'Hello There',
                                        'time_sent': int(time.mktime(time_in_future.timetuple()))})

    # Get dm message info
    message_response = requests.get(config.url + "dm/messages/v1",
                                    params={
                                        'token': register_response2['token'],
                                        'dm_id': dm_response['dm_id'],
                                        'start': 0
                                    })

    message_response = message_response.json()

    assert sendmessage.status_code == 200
    
    assert message_response['messages'] == []

# Check that if messages sent with sendlater and message_send in the same time
# frame do not have the same message_id
def test_message_sendlater_duplicate_message_ids(clear_data):

    # Register a user
    user = request_register("derrick@gmail.com", "password", "Golden", "Horse")
    user = user.json()

    # Create a channel
    channel = request_channels_create(user['token'], "channel1", False)
    channel = channel.json()

    # Create a dm
    dm = request_dm_create(user['token'], [])
    dm = dm.json()

    later_time = datetime.now() + timedelta(seconds = 2)
    later_time = int(time.mktime(later_time.timetuple()))

    # Set 1 message to be sent in the channel later
    msg1 = request_message_sendlater(user['token'], channel['channel_id'], "hello", later_time)

    # Set 2 messages to be sent in the dm later
    msg2 = request_message_sendlaterdm(user['token'], dm['dm_id'], "hello", later_time)
    msg3 = request_message_sendlaterdm(user['token'], dm['dm_id'], "hello", later_time)

    # Send a message with message/senddm/v1
    msg4 = request_message_senddm(user['token'], dm['dm_id'], "hello")
    
    # Send a message with message
    msg5 = request_message_send(user['token'], channel['channel_id'], "hello")

    msg1 = msg1.json()
    msg2 = msg2.json()
    msg3 = msg3.json()
    msg4 = msg4.json()
    msg5 = msg5.json()

    # Check that none of the message_ids are identical
    assert msg1['message_id'] != msg2['message_id'] != msg3['message_id'] != msg4['message_id'] != msg5['message_id'] 

