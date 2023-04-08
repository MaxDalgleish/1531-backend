import pytest
import requests
from src import config
from src.error import AccessError, InputError
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
def register_user_1():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'password123',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    return register_response.json()

def register_user_2():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'password123456',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    return register_response.json()

def register_user_3():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Derrick@gmail.com',
                                            'password': 'password000',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    return register_response.json()

# Test if invalid token raises an AccessError
def test_search_invalid_token(clear_data):

    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # Send a dm "Hello world!"
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello world!"})
    
    # Search the dm given an invalid token
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': invalid_token1(),
                                           'query_str': "Hello world!"})

    assert search_response.status_code == AccessError.code
    
# Test whether InputError is raised on empty query string
def test_search_empty_query(clear_data):
    
    # Register a user and save response
    register_response = register_user_1()
    token = register_response['token']

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'CatSociety',
                                           'is_public': False})
    channel_response = channel_response.json()

    # Send a message in the channel
    requests.post(config.url + "message/send/v1",
                  json={'token': token,
                        'channel_id': channel_response['channel_id'],
                        'message': "Never gonna give you up"})
    
    # Search the channel message given an empty query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token,
                                           'query_str': ""})

    assert search_response.status_code == InputError.code

# Test whether InputError raised on query string with length over 1000
def test_search_query_len_over_1000(clear_data):
    
    # Register a user and save response
    register_response = register_user_1()
    token = register_response['token']

    # Create a channel and save response
    channel_response = requests.post(config.url + "channels/create/v2",
                                     json={'token': register_response['token'],
                                           'name': 'SpookSoc',
                                           'is_public': False})
    channel_response = channel_response.json()

    # Send a message in the channel
    requests.post(config.url + "message/send/v1",
                  json={'token': register_response['token'],
                        'channel_id': channel_response['channel_id'],
                        'message': "Spooky Scary Skeleton"})
    
    # Search the channel message given a query string over 1000 characters long
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token,
                                           'query_str': "p10LiqPptwrkoRTPYs0yZP9dABPEiqebu6DCKheVXxOlrqbnksGZhyWbayt0ZKvDOxXdSJaHaO5i1Q2GSZSVwce3HlvCKHCSdqqoUzkQDMjkH0SDsucOZUscE1qRhejLnxL4xbWqQKQm4DU5Dll9WWq6Xi728ZuvzK5XUCfCOkHSak8xHsI3R2xJq5u2H9NBjRa5Y5ZDp1ghKMbB7X5CLYWZaJcKLyXPUxNO0fcV6RYPBhC2eE5zIS2gijBLOUQ3JHZrJVEvsdqE0ld3zw7AVa3uMyfLP5TwMgkgivi6cqER0O6wkeS4kNeFil3YC3Fr7dabbsIakHQfC9l8VhodkGGywc4N8iX3MTKdGVeEpI3DKYYRSHNEMq6QTxfUPzYN7ay0fQBrVMT3fWY2YFscXmJBpzdpWRHyX4g5MMKCzQhw2j4RemJZFD3JnR40Qk2bwL4STpNCmctgAeHrzRAF6TwpvgXGGBrmxbFxJQy4VsL8WIVgaXMosaAIcPzByDf8srtiem8WWmkx0itNu5AFKCcULtjoHLpzzFIMNW3caq9QlU2eMG6Zz4cqffTq0QqdoeUjioRQic2ldrlawr9PJJdxTtN9nYrziNnGAakVXztoynhltgxNPE3oEQiHoRNU33Sp5uTPyafOuIFj4sqfgZJLr7BbXbdKob9M7QxX1BOsYdKbGmTk5nZ5ydFfIXTS10nuqRAMzXB4Oov7sns702W8B3m0yZ8gMOkAIzYNgy2yCzkqrWzsYBncYpomX694YDHszoyCvU76NkiQS32nLKsOzip2i87i6Rf7FtUqwJOcgcZRUOKztvn84bnptQgRYBxeNuBHEKojdJOImhMJHHv5Kbc90RVjVHNZujQhmNQmVAVMC58g8wE5E8ibAcll6LyYI38hCBVVrMI9L1FHwkodXJf1uuGHWMQtXDcEtGDRVTMQwWOMSv3WCbCxPU1MUANFLQx9ocoNN3HpirKXzKthbrJjKB1aYsksaCEDW"})

    assert search_response.status_code == InputError.code

# Test if dm messages are returned correctly when searched
def test_search_dm_messages(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # User1 creates a dm with user2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_register_2]})
    dm_create_response = dm_create_response.json()

    # User2 sends dm 51 times, which is a string of a number from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/senddm/v1",
                  json={'token': token2,
                        'dm_id': dm_create_response['dm_id'],
                        'message': str(message)})
    
    # User 1 searches the dm message given the query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token1,
                                           'query_str': "5"})
    search_response = search_response.json()
    
    assert search_response['messages'][0]['u_id'] == auth_register_2
    assert search_response['messages'][0]['message'] == "5"
    assert search_response['messages'][0]['message_id'] == 5

# Test if dm messages are returned correctly when searched by a user who is not
# a part of the dm
def test_search_dm_messages_user_not_in(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = register_user_3()
    token3 = register_response3['token']
    
    # User1 creates a dm with user2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_register_2]})
    dm_create_response = dm_create_response.json()

    # User2 sends dm 51 times, which is a string of number from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/senddm/v1",
                  json={'token': token2,
                        'dm_id': dm_create_response['dm_id'],
                        'message': str(message)})
    
    # User 3 searches the dm message given the query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token3,
                                           'query_str': "5"})
    search_response = search_response.json()
    
    assert search_response['messages'] == []
    
# Test if channel messages are returned correctly when searched
def test_search_channel_messages(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # User1 creates a channel
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Channel_0',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})

    # User2 sends message 51 times, which is a string of numbers from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/send/v1",
                  json={'token': token2,
                        'channel_id': channel_id,
                        'message': str(message)})
    
    # User1 searches the channel message given the query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token1,
                                           'query_str': "9"})
    search_response = search_response.json()
    
    assert search_response['messages'][0]['u_id'] == auth_register_2
    assert search_response['messages'][0]['message'] == "9"
    assert search_response['messages'][0]['message_id'] == 9

# Test if dm messages are returned correctly when searched by a user who is not
# a part of the channel
def test_search_channel_messages_user_not_in(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    
    # Register user3 and save response
    register_response3 = register_user_3()
    token3 = register_response3['token']
    
    # User1 creates a channel
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Channel_0',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})

    # User2 sends message 51 times, which is a string of numbers from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/send/v1",
                  json={'token': token2,
                        'channel_id': channel_id,
                        'message': str(message)})
    
    # User3 searches the channel message given the query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token3,
                                           'query_str': "9"})
    search_response = search_response.json()
    
    assert search_response['messages'] == []

# Test if sending messages to both dm and channels can be searched correctly
def test_search_dm_and_channel_messages(clear_data):
    
    # Register user1 and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_register_2 = register_response2['auth_user_id']
    
    # User1 creates a channel
    channel_create_response = requests.post(config.url + 'channels/create/v2',
                                            json={'token': token1,
                                                  'name': 'Channel_0',
                                                  'is_public': True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    requests.post(config.url + 'channel/join/v2',
                  json={'token': token2,
                        'channel_id': channel_id})
    
    # User2 sends message 51 times, which is a string of numbers from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/send/v1",
                  json={'token': token2,
                        'channel_id': channel_id,
                        'message': str(message)})
    
    # User1 creates a dm with user2
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_register_2]})
    dm_create_response = dm_create_response.json()

    # User2 sends dm 51 times, which is a string of numbers from 1 to 51
    for message in range(1, 52):
        requests.post(config.url + "message/senddm/v1",
                  json={'token': token2,
                        'dm_id': dm_create_response['dm_id'],
                        'message': str(message)})
    
    # User 1 searches the dm message given the query string
    search_response = requests.get(config.url + "search/v1",
                                   params={'token': token1,
                                           'query_str': "7"})
    search_response = search_response.json()

    print(search_response)
    
    assert search_response['messages'][0]['u_id'] == auth_register_2
    assert search_response['messages'][0]['message'] == "7"
    assert search_response['messages'][0]['message_id'] == 7

    assert search_response['messages'][1]['message'] == "17"
    assert search_response['messages'][2]['message'] == "27"
    assert search_response['messages'][3]['message'] == "37"
    assert search_response['messages'][4]['message'] == "47"
    
    assert search_response['messages'][5]['u_id'] == auth_register_2
    assert search_response['messages'][5]['message'] == "7"
    assert search_response['messages'][5]['message_id'] == 58

    assert search_response['messages'][6]['message'] == "17"
    assert search_response['messages'][7]['message'] == "27"
    assert search_response['messages'][8]['message'] == "37"
    assert search_response['messages'][9]['message'] == "47"
