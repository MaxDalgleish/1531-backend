import pytest
import requests 
from src import config
from tests.test_helpers import invalid_token3

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
def test_dm_list_invalid_token(clear_data):

    # Call dm list and get response
    dm_response = requests.get(config.url + "dm/list/v1",
                               params={'token': invalid_token3()})

    assert dm_response.status_code == 403
    
# Test if empty dms is returned when no dms were created
def test_dm_list_empty(clear_data):
    
    # Register a user
    register_response = register_user_1()
    
    # Call dm list and get response
    dm_response = requests.get(config.url + "dm/list/v1",
                                params={'token': register_response['token']})
    
    assert dm_response.json() == {'dms': []}

# Test if correct list of dm is returned given one dm was created
def test_dm_list_one_dm_sent(clear_data):
    
    # Register 2 users and save response
    register_response1 = register_user_1()
    register_response2 = register_user_2()
    
    # Create a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1",
                                       json={'token': register_response1['token'],
                                             'u_ids': [register_response2['auth_user_id']]})
    dm_create_response_data = dm_create_response.json()

    # Call dm list and get response
    dm_list_response = requests.get(config.url + "dm/list/v1",
                                    params={'token': register_response1['token']})
    dm_list_response = dm_list_response.json()
    
    assert dm_list_response == {'dms': [{'dm_id': dm_create_response_data['dm_id'],
                                         'name': 'derrickdoan, justinson'}]}
