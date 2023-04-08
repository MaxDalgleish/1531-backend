import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test where the token is invalid
def test_invalid_token(clear_data):
    
    removeowner_response = requests.post(config.url + "channel/removeowner/v1", 
                  json = {'token': invalid_token1(), "channel_id": 1, "u_id": 1})
    
    assert removeowner_response.status_code == 403

# Test when a global owner isn't a member of a channel
def test_global_owner_not_channel_member(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register user2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',
                        json = {'email': 'thirdemail@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Alex',
                                'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # User2 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})                    
    
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response2['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})

    removeowner_response = requests.post(config.url + 'channel/removeowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})
    assert removeowner_response.status_code == 403                                 

# Test when a user isn't a channel owner
def test_user_not_channel_owner(clear_data):
    # Register a new user
    register_response1 = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response1 = register_response1.json()

    # Register user2
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',
                        json = {'email': 'thirdemail@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Alex',
                                'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # User1 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response1['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # User2 joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    # User3 joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    # User2 is added as a channel owner
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})

    # User3 attempts to remove user2 from being a channel owner
    removeowner_response = requests.post(config.url + 'channel/removeowner/v1',
                                    json = {'token': register_response3['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})
    assert removeowner_response.status_code == 403     

# Test when a channel_id doesn't refer to any channel
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

    removeowner_response = requests.post(config.url + 'channel/removeowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': 258,
                                            'u_id': register_response2['auth_user_id']})
    assert removeowner_response.status_code == 400

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

    removeowner = requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response1['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': 9000})
    assert removeowner.status_code == 400

# User ID refers to a user who isn't an owner of the channel and returns input error
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

    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    removeowner = requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response1['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': register_response2['auth_user_id']})
    assert removeowner.status_code == 400

# Token refers to someone who is not a global owner or channel owner
def test_token_not_channel_owner(clear_data):
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

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',
                        json = {'email': 'thirdemail@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Alex',
                                'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Second user creates a channel                               
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # Third User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    removeowner = requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response3['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': register_response2['auth_user_id']})
    assert removeowner.status_code == 403


# User ID refers to someone who is the only owner of a channel
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

    removeowner = requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response1['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': register_response1['auth_user_id']})

    assert removeowner.status_code == 400

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

    # Register a second user
    register_response2 = requests.post(config.url + 'auth/register/v2',  
               json = {'email': 'secondemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'Steven',
                        'name_last': 'Alex'})
    register_response2 = register_response2.json()

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',
                        json = {'email': 'thirdemail@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Alex',
                                'name_last': 'Steven'})
    register_response3 = register_response3.json()
    
    # Second User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response2['token'],
                        'channel_id': channel_response1['channel_id']})

    # Adding user2 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response2['auth_user_id']})

    # Third user joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    # Adding user3 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response1['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})
    
    requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response2['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': register_response3['auth_user_id']})

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
                                     },
                                     {   'u_id': register_response3['auth_user_id'],
                                         'email': 'thirdemail@gmail.com',
                                         'name_first': 'Alex',
                                         'name_last': 'Steven',
                                         'handle_str': 'alexsteven',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

# Test if a user is a global owner and can remove people from the owner permission
def test_global_owner(clear_data):
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

    # Register a third user
    register_response3 = requests.post(config.url + 'auth/register/v2',
                        json = {'email': 'thirdemail@gmail.com',
                                'password': 'validpassword',
                                'name_first': 'Alex',
                                'name_last': 'Steven'})
    register_response3 = register_response3.json()

    # Second user creates a new channel                             
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': register_response2['token'],
                                            'name': 'Channelone',
                                            'is_public': True})
    channel_response1 = channel_response1.json()

    # First User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response1['token'],
                        'channel_id': channel_response1['channel_id']})

    # Third User joins the channel
    requests.post(config.url + 'channel/join/v2',
                json = {'token': register_response3['token'],
                        'channel_id': channel_response1['channel_id']})

    # Adding user3 to the channel owners
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': register_response2['token'],
                                            'channel_id': channel_response1['channel_id'],
                                            'u_id': register_response3['auth_user_id']})

    # Removing user3 from the channel owners by the global owner
    requests.post(config.url + 'channel/removeowner/v1', 
                                json = {'token': register_response1['token'],
                                        'channel_id': channel_response1['channel_id'],
                                        'u_id': register_response3['auth_user_id']})

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
                                     },
                                     {   'u_id': register_response3['auth_user_id'],
                                         'email': 'thirdemail@gmail.com',
                                         'name_first': 'Alex',
                                         'name_last': 'Steven',
                                         'handle_str': 'alexsteven',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                        ]
                                }

    



