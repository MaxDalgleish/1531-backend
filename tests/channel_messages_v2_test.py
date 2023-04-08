import pytest
import requests
from src import config
from tests.test_helpers import invalid_token3

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test if accesserror is raised if token is invalid
def test_messages_v2_user_id_doesnt_exist(clear_data):
    
    # Register user and get the token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword123',
                                            'name_first': 'Justin',
                                            'name_last': 'Son'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token,
                                                  'name': 'Channel_1',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']

    # Get output from channel messages
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': invalid_token3(),
                                                     'channel_id': channel_id,
                                                     'start': 0})

    assert channel_messages_response.status_code == 403

# Test if inputerror is raised if channel_id does not exist
def test_messages_v2_channel_id_doesnt_exist(clear_data):

    # Register user and get the token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword123',
                                            'name_first': 'Justin',
                                            'name_last': 'Son'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Get messages response
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token,
                                                     'channel_id': 1,
                                                     'start': 0})

    assert channel_messages_response.status_code == 400

# Test if inputerror is raised if  does not refer to a valid channel
def test_messages_v2_channel_id_invalid(clear_data):

    # Register user and get their token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword123',
                                            'name_first': 'Justin',
                                            'name_last': 'Son'})
    register_response_data = register_response.json()
    token = register_response_data["token"]
    
    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token,
                                                  'name': 'Channel_1',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']

    # Get messages response
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token,
                                                     'channel_id': channel_id + 1,
                                                     'start': 0})

    assert channel_messages_response.status_code == 400

# Test if inputerror is raised if start is greater than the total number of messages
def test_messages_v2_channel_start_greater_than_total_messages(clear_data):

    # Register user and get the token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'justin@gmail.com',
                                            'password': 'validpassword123',
                                            'name_first': 'Justin',
                                            'name_last': 'Son'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token,
                                                  'name': 'Channel_3',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']

    # Get message response
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token,
                                                     'channel_id': channel_id,
                                                     'start': 2})
    
    assert channel_messages_response.status_code == 400

# Test if inputerror is raised if channel is valid but the user is not a member
# of the channel
def test_messages_v2_channel_id_valid_and_authorised_but_not_a_member(clear_data):

    # Register user 1 and get their token
    register_response1 = requests.post(config.url + 'auth/register/v2',
                                       json={'email': 'cynthia@gmail.com',
                                             'password': 'validpassword123',
                                             'name_first': 'Cynthia',
                                             'name_last': 'Li'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2 and get their token
    register_response2 = requests.post(config.url + 'auth/register/v2',
                                       json={'email': 'justin@gmail.com',
                                             'password': 'validpassword123',
                                             'name_first': 'Justin',
                                             'name_last': 'Son'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Channel_0',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']

    # Get messages response
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token2,
                                                     'channel_id': channel_id,
                                                     'start': 0})

    assert channel_messages_response.status_code == 403

# Test if end is returned as -1 if there are no more messages to load
def test_message_v2_no_more_messages(clear_data):

    # Register user and get token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'validpassword123',
                                            'name_first': 'Cynthia',
                                            'name_last': 'Li'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token,
                                                  'name': 'Channel_new',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # Get channel messages response
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token,
                                                     'channel_id': channel_id,
                                                     'start': 0})
    channel_messages_response_data = channel_messages_response.json()

    assert channel_messages_response_data['end'] == -1
            
# Test if channel message is returned correctly given different start values
def test_messages_v2_returned_comprehensive(clear_data):
    
    # Register user 1 and get their token
    register_response1 = requests.post(config.url + 'auth/register/v2',
                                       json={'email': 'cynthia@gmail.com',
                                             'password': 'validpassword123',
                                             'name_first': 'Cynthia',
                                             'name_last': 'Li'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2 and get their token
    register_response2 = requests.post(config.url + 'auth/register/v2',
                                       json={'email': 'justin@gmail.com',
                                             'password': 'validpassword123',
                                             'name_first': 'Justin',
                                             'name_last': 'Son'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    
    # Create channel and get channel id
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Channel_0',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User 2 joins channel
    requests.post(config.url + 'channel/join/v2',
                 json={'token': token2,
                       'channel_id': channel_id})
        
    # User 1 sends message 51 times
    for message in range(1, 52):
        requests.post(config.url + "message/send/v1",
                  json={'token': token1,
                        'channel_id': channel_id,
                        'message': str(message)})
        
    # user 2 gets messages with start 0
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token2,
                                                     'channel_id': channel_id,
                                                     'start': 0})
    channel_messages_response = channel_messages_response.json()
            
    # Check that messages are returned correctly
    for index in range(0, 50):
        assert channel_messages_response['messages'][index]['message'] == str(52 - index - 1)
            
    assert channel_messages_response['start'] == 0
    assert channel_messages_response['end'] == 50

    # user 2 gets messages with start 50
    channel_messages_response = requests.get(config.url + 'channel/messages/v2',
                                             params={'token': token2,
                                                     'channel_id': channel_id,
                                                     'start': 50})
    channel_messages_response = channel_messages_response.json()
    
    assert channel_messages_response['start'] == 50
    assert channel_messages_response['end'] == -1
    assert channel_messages_response['messages'][0]['message'] == '1'