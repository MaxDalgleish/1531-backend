import pytest
import requests
from src import config
from tests.test_helpers import invalid_token4

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test if AccessError status code is returned if token is invalid
def test_dm_create_invalid_token(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response = register_response.json()

    # Call dm/create/v1 with invalid token but valid u_id list
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': invalid_token4(),
                                             'u_ids': [register_response['auth_user_id']]})
    
    assert dm_create_response.status_code == 403
    
# Test if InputError is raised if a u_id in u_ids is invalid
def test_dm_u_id_invalid(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'password',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response = register_response.json()

    # Call dm/create/v1 with valid token but list of invalid u_ids
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': register_response['token'],
                                             'u_ids': [3940, 203, 29, 393]})
    
    assert dm_create_response.status_code == 400

# Test dm/create/v1 returns the correct dm_ids
def test_dm_create_return(clear_data):
    
    # Register 3 users and save response
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'max@gmail.com',
                                             'password': 'helloworld',
                                             'name_first': 'Max', 
                                             'name_last': 'Dalgeish'})

    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'allan@gmail.com',
                                             'password': 'password',
                                             'name_first': 'Allan', 
                                             'name_last': 'Zhang'})                    

    register_response3 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'justin@gmail.com',
                                             'password': 'thisisagoodpw',
                                             'name_first': 'Justin', 
                                             'name_last': 'Son'})                    

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()
    register_response3 = register_response3.json()

    # User1 creates a dm with user2 and user3
    dm_create_response1 = requests.post(config.url + "dm/create/v1", 
                                        json={'token': register_response1['token'],
                                              'u_ids': [register_response2['auth_user_id'],
                                                        register_response3['auth_user_id']]})

    # User2 creates a dm with user1 and user3
    dm_create_response2 = requests.post(config.url + "dm/create/v1", 
                                        json={'token': register_response2['token'],
                                              'u_ids': [register_response1['auth_user_id'],
                                                        register_response3['auth_user_id']]})

    # User3 creates a dm with user1 and user2
    dm_create_response3 = requests.post(config.url + "dm/create/v1", 
                                        json={'token': register_response3['token'],
                                              'u_ids': [register_response1['auth_user_id'],
                                                        register_response2['auth_user_id']]})

    assert dm_create_response1.json() == {'dm_id': 1}
    assert dm_create_response2.json() == {'dm_id': 2}
    assert dm_create_response3.json() == {'dm_id': 3}

# Test dm can be created with just one person
def test_dm_create_one_member(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                    json={'email': 'max@gmail.com',
                                          'password': 'helloworld',
                                          'name_first': 'Max', 
                                          'name_last': 'Dalgeish'})

    register_response = register_response.json()

    # Create a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': register_response['token'],
                                             'u_ids': []})

    assert dm_create_response.status_code == 200

# Test if correct name is stored when created
def test_dm_create_details_check_name(clear_data):
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                    json={'email': 'max@gmail.com',
                                          'password': 'helloworld',
                                          'name_first': 'Max', 
                                          'name_last': 'Dalgeish'})
    register_response = register_response.json()
    token = register_response['token']

    # Create a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token,
                                             'u_ids': []})
    dm_create_response_data = dm_create_response.json()
    dm_id = dm_create_response_data['dm_id']
    
    assert dm_create_response.status_code == 200
    
    # Call dm details and get response
    dm_details_response = requests.get(config.url + "dm/details/v1",
                                       params={'token': token,
                                               'dm_id': dm_id})
    dm_details_response = dm_details_response.json()
    
    assert dm_details_response == {
        'name': 'maxdalgeish',
        'members': [{'u_id': 1, 
                     'email': 'max@gmail.com',
                     'name_first': 'Max',
                     'name_last': 'Dalgeish',
                     'handle_str': 'maxdalgeish',
                     'profile_img_url': config.url + "static/default.jpg"
                     }]
        }
    
# Test that dm members include the owner
def test_dm_create_details_check_members(clear_data):

    # Register 2 users and save response
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'max@gmail.com',
                                            'password': 'helloworld',
                                            'name_first': 'Max', 
                                            'name_last': 'Dalgeish'})
    register_response1 = register_response1.json()
    token1 = register_response1['token']
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'justin@gmail.com',
                                             'password': 'thisisagoodpw',
                                             'name_first': 'Justin', 
                                             'name_last': 'Son'})
    register_response2 = register_response2.json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # Create a dm and save response
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                       json={'token': token1,
                                             'u_ids': [auth_user_id2]})
    dm_create_response_data = dm_create_response.json()
    dm_id = dm_create_response_data['dm_id']
    
    # user 2 calls dm details and get response
    dm_details_response = requests.get(config.url + "dm/details/v1",
                                       params={'token': token2,
                                               'dm_id': dm_id})
    dm_details_response = dm_details_response.json()

    assert dm_details_response == {'name': 'justinson, maxdalgeish',
                                   'members': [{'u_id': 1,
                                                'email': 'max@gmail.com',
                                                'name_first': 'Max',
                                                'name_last': 'Dalgeish',
                                                'handle_str': 'maxdalgeish',
                                                'profile_img_url': config.url + "static/default.jpg"
                                                },
                                               {'u_id': 2,
                                                'email': 'justin@gmail.com',
                                                'name_first': 'Justin',
                                                'name_last': 'Son',
                                                'handle_str': 'justinson',
                                                'profile_img_url': config.url + "static/default.jpg"
                                                }]}
