import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test if Access error is raised if the given token isn't valid
def test_channel_create_v2_no_user_id(clear_data):
    
    # Create a channel
    channel_response = requests.post(config.url + 'channels/create/v2', 
                                    json={'token': invalid_token2(),
                                          'name': 'Channel one',
                                          'is_public': True})
    
    assert channel_response.status_code == 403

# Test if inputerror arises when the name of the channel is greater than 20
def test_channel_create_v2_name_length_over_20(clear_data):
    
    # Register a user and get their token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'validemail@gmail.com', 
                                            'password': 'validpassword',
                                            'name_first': 'John',
                                            'name_last': 'Smith'})
    register_response_data = register_response.json()
    token = register_response_data['token']

    # Create a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                    json={'token': token,
                                          'name': 'abcedfghijklmnopqrstuvwxyz',
                                          'is_public': True})

    assert channel_response.status_code == 400

# Test if input error arises when name is an empty string
def test_channel_create_v2_no_name(clear_data):
    
    # Register a user and get their token
    register_response = requests.post(config.url + 'auth/register/v2',
                                      json={'email': 'validemail@gmail.com', 
                                            'password': 'validpassword',
                                            'name_first': 'John',
                                            'name_last': 'Smith'})
    register_response_data = register_response.json()
    token = register_response_data['token']

    # Creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2',
                                     json={'token': token,
                                           'name': '',
                                           'is_public': True})
    
    # Checking if the input error arises from the given input
    assert channel_response.status_code == 400

# Test if the creating a single channel works
def test_channel_create_v2_create_public(clear_data):
    
    # Register a user and get their token
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response_data = register_response.json()
    auth_user_id = register_response_data['auth_user_id']
    token = register_response_data['token']

    # Creates a channel and get channel id
    channel_response = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': token,
                                            'name': 'Validname',
                                            'is_public': True})
    channel_response_data = channel_response.json()
    channel_id = channel_response_data['channel_id']

    # Getting the details of the created channel
    details_response = requests.get(config.url + 'channel/details/v2',
                                    params={'token': token,
                                            'channel_id': channel_id})
    details_response = details_response.json()

    # Asserting that the channel details are correct
    assert details_response == {
                                 'name': 'Validname',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                    {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                    }
                                        ]
                                }

# # Test if creating multiple channels works
def test_channel_create_v2_create_multiple(clear_data):
    
    # Register a user
    register_response = requests.post(config.url + 'auth/register/v2', 
               json = {'email': 'validemail@gmail.com', 
                        'password': 'validpassword',
                        'name_first': 'John',
                        'name_last': 'Smith'})
    register_response = register_response.json()
    auth_user_id = register_response['auth_user_id']
    token = register_response['token']
                                     
    # User1 creates a channel
    channel_response1 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': token,
                                            'name': 'Channelone',
                                            'is_public': True})
    # User1 creates a second channel
    channel_response2 = requests.post(config.url + 'channels/create/v2',
                                    json = {'token': token,
                                            'name': 'Channeltwo',
                                            'is_public': False})
    
    # Get channel ids
    channel_response1 = channel_response1.json()
    channel_id1 = channel_response1['channel_id']
    channel_response2 = channel_response2.json()
    channel_id2 = channel_response2['channel_id']
    
    # Get details of the first channel
    details_response1 = requests.get(config.url + 'channel/details/v2',
                                     params={'token': token,
                                             'channel_id': channel_id1})
    # Get details of the second channel
    details_response2 = requests.get(config.url + 'channel/details/v2',
                                     params={'token': token,
                                             'channel_id': channel_id2})
    details_response1 = details_response1.json()
    details_response2 = details_response2.json()
    
    # Assert the details of the first channel are correct
    assert details_response1 == {
                                 'name': 'Channelone',
                                 'is_public': True,
                                 'owner_members': [
                                     {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                    {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                    }
                                        ]
                                }
    # Assert the details of the second channel are correct
    assert details_response2 == {
                                 'name': 'Channeltwo',
                                 'is_public': False,
                                 'owner_members': [
                                     {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                     }
                                                ], 
                                 'all_members':[
                                    {
                                         'u_id': auth_user_id,
                                         'email': 'validemail@gmail.com', 
                                         'name_first': 'John', 
                                         'name_last': 'Smith', 
                                         'handle_str': 'johnsmith',
                                         'profile_img_url': config.url + "static/default.jpg"
                                    }
                                        ]
                                }
