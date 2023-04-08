import pytest
import requests
import datetime
import time
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
def register_user_1():
    
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'hyunseo@gmail.com',
                                            'password': 'passwordispassword',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    return register_response.json()

def register_user_2():
    
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'idontknow',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    return register_response.json()

# Test if InputError status code is returned if dm is invalid
def test_dm_messages_invalid_dm(clear_data):
    
    register_response = register_user_1()
    token = register_response['token']
    
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token,
                                               'dm_id': 100,
                                               'start': 0})

    assert dm_message_response.status_code == 400
    
# Test if InputError status code is returned if dm is invalid
def test_dm_messages_invalid_token(clear_data):
    
    register_response = register_user_1()
    token = register_response['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': invalid_token2(),
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 0})

    assert dm_message_response.status_code == 403

# Test if AccessError is raised if dm id is valid, but the auth user is not a
# member of the dm
def test_dm_messages_id_valid_but_not_a_member(clear_data):
    
    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = register_user_2()
    token2 = register_response2['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # User 2 tries to access the dm, which they are not a part of
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 0})
    
    assert dm_message_response.status_code == 403
    
# Test if start is greater than the total number of messages in the dm
def test_dm_messages_start_is_greater_than_total_messages(clear_data):
    
    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm to user 2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()
    
    # Call message/senddm
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello world!"})
    
    # User 2 accesss the dm with start greater than number of messages
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 2})
    
    assert dm_message_response.status_code == 400

# Test if dm is returned correctly
def test_dm_messages_returned_correctly(clear_data):
    
    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    auth_user_id1 = register_response1['auth_user_id']
    
    # Register user 2
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm to user 2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()
    
    # Call message/senddm
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello World"})
    
    # user 2 gets dm messages with start 0
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 0})
    dm_message_response = dm_message_response.json()
    
    time_message = datetime.datetime.now()
    time_message = int(time.mktime(time_message.timetuple()))
    
    assert dm_message_response['start'] == 0
    assert dm_message_response['end'] == -1
    
    # check second message_is saved correctly (will be first in channel_messages list
    # as it is the most recent message)
    assert dm_message_response['messages'][0]['message_id'] == 1
    assert dm_message_response['messages'][0]['u_id'] == auth_user_id1
    assert dm_message_response['messages'][0]['message'] == "Hello World"
    
    # Check time_created is is within a second of the time the request was sent
    time_recorded = dm_message_response['messages'][0]['time_created']
    assert (time_message - time_recorded) < 2
    
    assert dm_message_response['messages'][0]['dm_id'] == 1     
            
# Test if dm messages are returned correctly given different start values
def test_dm_messages_returned_comprehensive(clear_data):
    
    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm to user 2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()

    # User 2 calls message/senddm 51 times
    for message in range(1, 52):
        requests.post(config.url + "message/senddm/v1",
                  json={'token': token2,
                        'dm_id': dm_create_response['dm_id'],
                        'message': str(message)})
        
    # user 2 gets dm messages with start 0
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 0})
    dm_message_response = dm_message_response.json()

    # Check that messages are returned correctly
    for index in range(0, 50):
        assert dm_message_response['messages'][index]['message'] == str(52 - index - 1)
            
    assert dm_message_response['start'] == 0
    assert dm_message_response['end'] == 50
            
    # user 2 gets dm messages with start 50
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id'],
                                               'start': 50})
    dm_message_response = dm_message_response.json()
            
    assert dm_message_response['start'] == 50
    assert dm_message_response['end'] == -1
    assert dm_message_response['messages'][0]['message'] == '1'