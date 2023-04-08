import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

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
def test_dm_details_invalid_token(clear_data):

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
    
    # Call dm details and get response
    dm_response = requests.get(config.url + "dm/details/v1",
                               params={'token': invalid_token1(),
                                       'dm_id': dm_create_response['dm_id']})

    assert dm_response.status_code == 403
    
# Test if invalid dm id raises an InputError
def test_dm_details_id_invalid(clear_data):
    
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
    
    # Call dm details and get response
    dm_response = requests.get(config.url + "dm/details/v1",
                               params={'token': token1,
                                       'dm_id': dm_create_response['dm_id'] + 1})
    
    assert dm_response.status_code == 400

# Test if AccessError is raised when the dm id is valid, but the user isnt a
# member of the dm
def test_dm_details_id_valid_but_not_member(clear_data):
    
    # Register 2 users and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    register_response2 = register_user_2()
    token2 = register_response2['token']
    
    # User 1 creates a dm to themself
    dm_create_response = requests.post(config.url + "dm/create/v1",
                                       json={'token': token1,
                                             'u_ids': []})
    dm_create_response = dm_create_response.json()

    # Call message/senddm
    requests.post(config.url + "message/senddm/v1",
                  json={'token': token1,
                        'dm_id': dm_create_response['dm_id'],
                        'message': "Hello world!"})
    
    # Call dm details and get response
    dm_response = requests.get(config.url + "dm/details/v1",
                               params={'token': token2,
                                       'dm_id': dm_create_response['dm_id']})
    
    assert dm_response.status_code == 403

# Test if the returned dm details is correct
def test_dm_details_correct_information(clear_data):
    
    # Register 2 users and save response
    register_response1 = register_user_1()
    token1 = register_response1['token']
    
    register_response2 = register_user_2()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User 1 creates a dm to user 2
    dm_create_response = requests.post(config.url + "dm/create/v1",
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response = dm_create_response.json()
    
    # Call dm details and get response
    dm_details_response = requests.get(config.url + "dm/details/v1",
                                       params={'token': token2,
                                               'dm_id': dm_create_response['dm_id']})
    dm_response = dm_details_response.json()
    
    assert dm_response == {
        'name': 'derrickdoan, justinson',
        'members': [{'u_id': 1, 
                     'email': 'derrick@gmail.com',
                     'name_first': 'Derrick',
                     'name_last': 'Doan',
                     'handle_str': 'derrickdoan',
                     'profile_img_url': config.url + "static/default.jpg"}, 
                    {'u_id': 2,
                     'email': 'justin@gmail.com',
                     'name_first': 'Justin',
                     'name_last': 'Son',
                     'handle_str': 'justinson',
                     'profile_img_url': config.url + "static/default.jpg"}
                    ]
        }