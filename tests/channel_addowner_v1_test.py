import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test where the token is invalid
def test_invalid_token(clear_data):
    addowner_response = requests.post(config.url + "channel/addowner/v1", 
                  json = {'token': invalid_token2(), "channel_id": 1, "u_id": 1})
    
    assert addowner_response.status_code == 403

# Test when a user isn't an owner of a channel
def test_user_not_channel_owner(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # User1 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})
    
    channeljoin_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response2['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})
    
    assert channeljoin_response.status_code == 403

#Test when a channel_id doesn't refer to any channel
def test_channelid_invalid(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    channeljoin_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': 258,
                                            'u_id': register_response2['auth_user_id']})
    assert channeljoin_response.status_code == 400

# User id does not refer to a valid user and an input error is raised
def test_invalid_user_id(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()
    
    #invalid ID is added to the channel owners
    channeljoin_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': 287})
    assert channeljoin_response.status_code == 400

# Test where the user inputting token is not a member of the channel
def test_token_not_channel_member(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    #Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Third user creates a new channel
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # First user creates a new channel                             
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # Making the second user join the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    # Trying to add user as an owner who isn't a member of the channel
    channeljoin_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response3['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})
    assert channeljoin_response.status_code == 403

# User ID refers to a user who isn't a member of the channel and returns input error
def test_not_channel_member(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    #Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # Adding user who isn't a member of the channel
    channeljoin_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})
    assert channeljoin_response.status_code == 400

# User ID refers to someone who is already an owner of the channel and returns input error
def test_already_channel_owner(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    #Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})
    

    # Adding user2 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                json = {'token': register_response1['token'],
                        'channel_id': channel_response1['channel_id'],
                        'u_id': register_response2['auth_user_id']})

    #Checking channel_details
    channel_details = requests.get(config.url + 'channel/details/v2',
                 params={'token': register_response1['token'],
                         'channel_id': channel_response1['channel_id']})
    channel_details = channel_details.json()

    # Adding user2 again to the channel owners list
    channeljoin_response1 = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})

    # Checking channel_details
    channel_details1 = requests.get(config.url + 'channel/details/v2',
                 params={'token': register_response1['token'],
                         'channel_id': channel_response1['channel_id']})
    channel_details1 = channel_details1.json()
   

    assert channeljoin_response1.status_code == 400

# Test if the function works properly
def test_addowner_succesful_test(clear_data):

    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    #Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()
    
    # Second User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    # Adding user2 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})

    # Checking channel_details
    details_response = requests.get(config.url + 'channel/details/v2',
                                    params={'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id']})
    details_response = details_response.json()
    # Assert the details of the channel details is correct
    assert details_response == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                    {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                    },
                                    {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

# Test if a user is a global owner and can add themselves to the channel
def test_global_owner(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # First User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response1['token'],
                        'channel_id': channel_response1['channel_id']})

    # Adding user1 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response1['auth_user_id']})

    # Checking channel_details
    details_response = requests.get(config.url + 'channel/details/v2',
                                    params={'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id']})
    details_response = details_response.json()
    
    # Assert the details of the channel details is correct
    assert details_response == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                     {
                                         'u_id': register_response2['auth_user_id'],
                                         'email': 'secondemail@gmail.com',
                                         'name_first': 'Steven',
                                         'name_last': 'Alex',
                                         'handle_str': 'stevenalex',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     },
                                     {
                                         'u_id': register_response1['auth_user_id'],
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

def test_global_owner_non_member_cant_addowner_public(clear_data):

    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Attempting to add user three to channel owners while user1 isn't a channel member
    addowner_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})
    assert addowner_response.status_code == 403

def test_global_owner_non_member_cant_addowner_private(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Create new channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': False})
    channel_response1 = channel_response1.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'thirdemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Alex',
                        'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Attempting to add user three to channel owners while user1 isn't a channel member
    addowner_response = requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})
    assert addowner_response.status_code == 403