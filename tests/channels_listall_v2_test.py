import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1, invalid_token3

@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Test if Access error arises when the given user_id isn't valid
def test_channel_listall_v2_user_id(clear):

    # Send get request for all channels for the non existing user is in
    list_response = requests.get(config.url + "channels/listall/v2",
                                    params={'token': invalid_token3()})

    # Check AccessError status code is returned
    assert list_response.status_code == 403

# Test is there is no channels created
def test_channels_listall_v2_no_channels(clear):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Send get request for all channels the user is in
    list_response = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token})
    list_response = list_response.json()

    # Check if an empty list is returned
    assert list_response == {"channels": []}

# Testing the first channel the user themselves created
def test_channels_listall_v2_list_first_channel_create(clear):
    
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data = register_response.json()
    token = register_response_data["token"]
    
    # Create a channel and store response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Channel New',
                                           'is_public': True})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']
   
    # Get response on channels/list/v2
    list_response = requests.get(config.url + "channels/listall/v2",
                                    params={'token': token})

    list_response = list_response.json()     

    # Test if correct channel details returned
    assert list_response == {"channels": [{"channel_id": channel_id, 
                                            "name": "Channel New"}]}                         

# Test if Access error arises when the given token isn't valid
def test_invalid_token(clear):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data = register_response.json()
    token = register_response_data["token"]                       
    
    # Create a channel
    requests.post(config.url + "channels/create/v2",
                  json={'token': token,
                        'name': 'Channel New',
                        'is_public': True})
   
    # Get response on channels/list/v2 with invalid token
    list_response = requests.get(config.url + "channels/listall/v2",
                                 params={'token': invalid_token1()})

    # Check AccessError status code is returned
    assert list_response.status_code == 403

def test_channels_listall_v2_list_first_private_create(clear):
    
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Create a channel and store response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Channel New',
                                           'is_public': False})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']
    
    # Get response on channels/list/v2      
    list_response = requests.get(config.url + "channels/list/v2",
                                    params={'token': token})
    list_response = list_response.json()     

    # Test if correct channel details returned
    assert list_response == {"channels": [{"channel_id": channel_id, 
                                            "name": "Channel New"}]}        

# Testing when one user creates multiple channels
def test_channels_listall_v2_list_multi_channel(clear):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data = register_response.json()
    token = register_response_data["token"]

    # Create three channels and store responses
    channel_response1 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Channel 1',
                                           'is_public': True})

    channel_response2 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Channel 2',
                                           'is_public': False}) 

    channel_response3 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token,
                                           'name': 'Channel 3',
                                           'is_public': True})         

    # Get channel ids
    channel_response1 = channel_response1.json()
    channel_id1 = channel_response1['channel_id']
    channel_response2 = channel_response2.json()
    channel_id2 = channel_response2['channel_id']
    channel_response3 = channel_response3.json()
    channel_id3 = channel_response3['channel_id']          

    # Get response on channels/list/v2
    list_response = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token})
    list_response = list_response.json()  

    assert list_response == {"channels": [
                                {"channel_id": channel_id1, 
                                "name": "Channel 1"},
                                {"channel_id": channel_id2, 
                                "name": "Channel 2"},
                                {"channel_id": channel_id3, 
                                "name": "Channel 3"},
                                ]}     

# Testing when user 1 created a channel but user 2 try to call the list function
# but is not in any channels
def test_channels_listall_v2_list_user_in_no_channel(clear):

    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel_2@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Moe'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"] 

    # Create a channel and store response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'Channel New',
                                           'is_public': True})
    channel_response = channel_response.json()
    channel_id = channel_response['channel_id']

    # Get response on channels/listall/v2
    list_response = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token2})
    list_response = list_response.json()

    # Check if channel info is returned
    assert list_response == {"channels": [{"channel_id": channel_id, 
                                           "name": "Channel New"}]}   

# Testing when mulitple users are in more than one channel through invite and
# join function
def test_channels_listall_v2_list_multiple_channels(clear):

    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Doe'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]

    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel_2@gmail.com',
                                            'password': 'password',
                                            'name_first': 'John', 
                                            'name_last': 'Moe'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    
    # Register user 3
    register_response3 = requests.post(config.url + "auth/register/v2",
                                      json={'email': 'channel_3@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Jane', 
                                            'name_last': 'Moe'})
    register_response_data3 = register_response3.json()
    token3 = register_response_data3["token"] 
   
    # Create a channel and store responses
    channel_response1 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token1,
                                           'name': 'Channel 1',
                                           'is_public': True})
    channel_response1 = channel_response1.json()
    channel_id1 = channel_response1['channel_id']

    # Create a channel and store responses
    channel_response2 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token2,
                                           'name': 'Channel 2',
                                           'is_public': True})
    channel_response2 = channel_response2.json()
    channel_id2 = channel_response2['channel_id']

    # Create a channel and store responses
    channel_response3 = requests.post(config.url + "channels/create/v2",
                                     json={'token': token3,
                                           'name': 'Channel 3',
                                           'is_public': False})
    channel_response3 = channel_response3.json()
    channel_id3 = channel_response3['channel_id']

    # User 3 joins channel 1
    requests.post(config.url + "channel/join/v2", 
                  json={'token': token3,
                        "channel_id": channel_response1["channel_id"]})

    # User 3 joins channel 2
    requests.post(config.url + "channel/join/v2", 
                  json={'token': token3,
                        "channel_id": channel_response2["channel_id"]})

    # User 3 invites user 2 to join Channel 3
    requests.post(config.url + "channel/invite/v2",
                 json={'token': token3, 
                       "channel_id": channel_id3, 
                       "u_id": token2})
    
    # User 2 joins channel 1
    requests.post(config.url + "channel/join/v2", 
                  json={'token': token2,
                        "channel_id": channel_id1})

    # Get response on channels/list/v2 for user 1
    list_response1 = requests.get(config.url + "channels/listall/v2",
                                  params={'token': token1})
    list_response1 = list_response1.json()

    # Get response on channels/list/v2 for user 2
    list_response2 = requests.get(config.url + "channels/listall/v2",
                                  params={'token': token2})
    list_response2 = list_response2.json()

    # Get response on channels/list/v2 for user 3
    list_response3 = requests.get(config.url + "channels/listall/v2",
                                  params={'token': token3})
    list_response3 = list_response3.json()

    # Check user 1 return list
    assert list_response1 == {"channels": [
                                            {"channel_id": channel_id1, 
                                            "name": "Channel 1"},
                                            {"channel_id": channel_id2, 
                                            "name": "Channel 2"},
                                            {"channel_id": channel_id3, 
                                            "name": "Channel 3"}
                                        ]}

    # Check user 2 return list
    assert list_response2 == {"channels": [
                                            {"channel_id": channel_id1, 
                                            "name": "Channel 1"},
                                            {"channel_id": channel_id2, 
                                            "name": "Channel 2"},
                                            {"channel_id": channel_id3, 
                                            "name": "Channel 3"}
                                        ]}

    # Check user 3 return list
    assert list_response3 == {"channels": [
                                            {"channel_id": channel_id1, 
                                            "name": "Channel 1"},
                                            {"channel_id": channel_id2, 
                                            "name": "Channel 2"},
                                            {"channel_id": channel_id3, 
                                            "name": "Channel 3"}
                                        ]}                 





