import pytest
import requests
from src import config
from tests.test_helpers import invalid_token4

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
def register_user_1():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    return register_response.json()

def register_user_2():
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'password123',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    return register_response.json()
    
# Test if invalid token raises an AccessError
def test_dm_remove_invalid_token(clear_data):

    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # Call message/senddm
    message_response = requests.post(config.url + "message/senddm/v1",
                                     json={'token': token1,
                                           'dm_id': dm_create_response['dm_id'],
                                           'message': "Hello world!"})
    message_response = message_response.json()
    
    # Call dm remove and get response
    dm_response = requests.delete(config.url + "dm/remove/v1",
                                  json={'token': invalid_token4(),
                                        'dm_id': dm_create_response['dm_id']})

    assert dm_response.status_code == 403
    
# Test if invalid dm id raises an InputError
def test_dm_remove_id_invalid(clear_data):
    
    # Register user 1
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()
    
    # Call message/senddm
    message_response = requests.post(config.url + "message/senddm/v1",
                                     json={'token': token1,
                                           'dm_id': dm_create_response['dm_id'],
                                           'message': "Hello world!"})
    message_response = message_response.json()

    # Call dm remove and get response
    requests.delete(config.url + "dm/remove/v1",
                    json={'token': token1, 'dm_id': dm_create_response['dm_id']})
    
    # Call dm remove again and get response
    dm_response = requests.delete(config.url + "dm/remove/v1",
                                  json={'token': token1,
                                        'dm_id': dm_create_response['dm_id']})
    
    assert dm_response.status_code == 400

# Test if AccessError is raised when the dm id is valid, but the user isnt the 
# dm creator
def test_dm_remove_id_valid_but_not_creator(clear_data):
    
    # Register 2 users and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1",
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()

    # Call message/senddm
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello world!"})
    
    # Call dm remove and get response
    dm_response = requests.delete(config.url + "dm/remove/v1",
                                  json={'token': token2,
                                        'dm_id': dm_create_response['dm_id']})
    
    assert dm_response.status_code == 403

# Test if dm is removed properly
def test_dm_remove_working_correctly(clear_data):
    
    # Register 2 users and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1",
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()

    # Call message/senddm
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello There!"})
    
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token2,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "General Kenobi!"})
    
    # Call dm remove and get response
    dm_response = requests.delete(config.url + "dm/remove/v1",
                                  json={'token': token1,
                                        'dm_id': dm_create_response['dm_id']})
    dm_response = dm_response.json()    
    
    assert dm_response == {}