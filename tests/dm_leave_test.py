import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test whether AcessError status code is returned when token is invalid
def test_dm_leave_invalid_token(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Harrypotter@gmail.com',
                                            'password': 'Hufflepuff',
                                            'name_first': 'Harry', 
                                            'name_last': 'Potter'})
    
    register_response = register_response.json()

    # Create a dm with just themself
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response['token'],
                                      'u_ids': []})
    
    dm_response = dm_response.json()

    # Call dm_leave with valid dm_id but invalid token
    leave_response = requests.post(config.url + "dm/leave/v1",
                                   json={'token': invalid_token2(),
                                         'dm_id': dm_response['dm_id']})

    assert leave_response.status_code == 403

# Test whether InputError is raised when dm_id does not refer to a valid dm
def test_dm_leave_invalid_dm_id(clear_data):
    
    # Register a user
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Haydnesmith@gmail.com',
                                            'password': 'comp1531',
                                            'name_first': 'Hayden', 
                                            'name_last': 'Smith'})
    
    register_response = register_response.json()

    # call dm leave with an invalid dm_id
    leave_response = requests.post(config.url + "dm/leave/v1",
                                   json={'token': register_response['token'],
                                         'dm_id': 50000})

    assert leave_response.status_code == 400
   

# Test whether AccessError is raised when dm_id is valid but auth_user is not a
# member of the dm
def test_dm_leave_not_a_member(clear_data):
    
    # Register 3 users
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Haydnesmith@gmail.com',
                                             'password': 'comp1531',
                                             'name_first': 'Hayden', 
                                             'name_last': 'Smith'})

    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Harrypotter@gmail.com',
                                             'password': 'Hufflepuff',
                                             'name_first': 'Harry', 
                                             'name_last': 'Potter'})

    register_response3 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'pokemon@gmail.com',
                                             'password': 'charizard',
                                             'name_first': 'Ash', 
                                             'name_last': 'Ketchum'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()
    register_response3 = register_response3.json()

    # User1 creates a dm with user2
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})
    
    dm_response = dm_response.json()

    # User3 calls dm leave on the dm but they are not a member of the dm
    leave_response = requests.post(config.url + "dm/leave/v1",
                                   json={'token': register_response3['token'],
                                         'dm_id': dm_response['dm_id']})

    assert leave_response.status_code == 403

# Test a member can leave a dm and and empty dictionary is returned
def test_dm_leave_member_can_leave(clear_data):
    
    # Register 2 users
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Haydnesmith@gmail.com',
                                             'password': 'comp1531',
                                             'name_first': 'Hayden', 
                                             'name_last': 'Smith'})
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Harrypotter@gmail.com',
                                             'password': 'Hufflepuff',
                                             'name_first': 'Harry', 
                                             'name_last': 'Potter'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User1 creates a dm with user2
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})
    
    dm_response = dm_response.json()

    # User2 calls dm leave
    leave_response = requests.post(config.url + "dm/leave/v1",
                                   json={'token': register_response2['token'],
                                         'dm_id': dm_response['dm_id']})

    assert leave_response.json() == {}

# Test that the member is not listed in members list with dm_details
def test_dm_leave_stored_correctly(clear_data):

    # Register 2 users
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'haydensmith@gmail.com',
                                             'password': 'comp1531',
                                             'name_first': 'Hayden', 
                                             'name_last': 'Smith'})
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Harrypotter@gmail.com',
                                             'password': 'Hufflepuff',
                                             'name_first': 'Harry', 
                                             'name_last': 'Potter'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User1 creates a dm with user2
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})
    
    dm_response = dm_response.json()

    # User 2 calls dm/leave
    requests.post(config.url + "dm/leave/v1",
                  json={'token': register_response2['token'],
                        'dm_id': dm_response['dm_id']})

    # User1 calls dm/details, the name should not be changed and the members 
    # list should not include user2
    details_response = requests.get(config.url + "dm/details/v1",
                                    params={'token': register_response1['token'],
                                            'dm_id': dm_response['dm_id']})
    
    assert details_response.json() == {     
                                        'name': "harrypotter, haydensmith",
                                        'members': [
                                            {'u_id': register_response1['auth_user_id'],
                                             'email': "haydensmith@gmail.com",
                                             'name_first': "Hayden",
                                             'name_last': "Smith",
                                             'handle_str': "haydensmith",
                                             'profile_img_url': config.url + "static/default.jpg"}
                                        ]
                                    }

# Test that the creator of the dm can leave and is not in members list with 
# dm_details
def dm_leave_creator_can_leave(clear_data):
    
    # Register 2 users
    register_response1 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Haydnesmith@gmail.com',
                                             'password': 'comp1531',
                                             'name_first': 'Hayden', 
                                             'name_last': 'Smith'})
    
    register_response2 = requests.post(config.url + "auth/register/v2", 
                                       json={'email': 'Harrypotter@gmail.com',
                                             'password': 'Hufflepuff',
                                             'name_first': 'Harry', 
                                             'name_last': 'Potter'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User1 creates a dm with user2
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response1['token'],
                                      'u_ids': [register_response2['auth_user_id']]})
    
    dm_response = dm_response.json()

    # User1 leaves the dm
    leave_response = requests.post(config.url + "dm/leave/v1",
                                   json={'token': register_response1['token'],
                                         'dm_id': dm_response['dm_id']})

    assert leave_response.status_code == 200

    # User2 calls dm details
    details_response = requests.get(config.url + "dm/details/v1",
                                    params={'token': register_response2['token'],
                                            'dm_id': dm_response['dm_id']})
    
    assert details_response.json() == {     
                                        'name': "haydensmith, harrypotter",
                                        'members': [
                                            {'u_id': register_response2['auth_user_id'],
                                             'email': "harrypotter@gmail.com",
                                             'name_first': "Harry",
                                             'name_last': "Potter",
                                             'handle': "harrypotter",
                                             'profile_img_url': config.url + "static/default.jpg"
                                             }
                                        ]
                                    }


# Test that dm no longer shows up in dm/list/v1 after a member has left
def test_dm_leave_not_in_list(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Haydnesmith@gmail.com',
                                            'password': 'comp1531',
                                            'name_first': 'Hayden', 
                                            'name_last': 'Smith'})

    register_response = register_response.json()

    # User creates a dm with just themself
    dm_response = requests.post(config.url + "dm/create/v1",
                                json={'token': register_response['token'],
                                      'u_ids': []})
    
    dm_response = dm_response.json()

    # User1 leaves the dm
    requests.post(config.url + "dm/leave/v1",
                  json={'token': register_response['token'],
                        'dm_id': dm_response['dm_id']})

    # User1 calls dm/list/v1, it should return an empty list
    list_response = requests.get(config.url + "dm/list/v1",
                                 params={'token': register_response['token']})

    assert list_response.json() == {'dms': []}


