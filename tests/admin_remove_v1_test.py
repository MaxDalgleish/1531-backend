import pytest
import requests 
from src import config
from tests.test_helpers import invalid_token2

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Invalid token
def test_admin_remove_v1_invalid_token(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    auth_user_id = register_response_data1["auth_user_id"]

    # Remove user but has invalid token
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': invalid_token2(),
                                       'u_id': auth_user_id})

    assert remove_response.status_code == 403

# U_id does not refer to a valid user
def test_admin_remove_v1_invalid_user(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    auth_user_id = register_response_data2["auth_user_id"]

    # Remove user with incorrect u_id
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id + 1})

    assert remove_response.status_code == 400

# U_id refers to a user who is the only global owner and are removing themselves
def test_admin_remove_v1_only_global_owner(clear_data):

    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id1 = register_response_data1["auth_user_id"]

	# Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
										json={'email': 'derrick@gmail.com',
											'password': 'validpassword1',
											'name_first': 'Derrick', 
											'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data1["token"]
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Change user2 to global owner
    change_response1 = requests.post(config.url + 'admin/userpermission/change/v1',
									json={'token': token1,
										'u_id': auth_user_id2,
										'permission_id': 1})

    assert change_response1.status_code == 200
    # User 2 removes themselves
    remove_response1 = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token2,
                                       'u_id': auth_user_id2})

    assert remove_response1.status_code == 200

    # User 1 removes themselves but fails, only global owner
    remove_response2 = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id1})

    assert remove_response2.status_code == 400

# The authorised user is not a global owner
def test_admin_remove_v1_not_global_owner(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    auth_user_id = register_response_data1["auth_user_id"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token1 = register_response_data2["token"]

    # User 2 tries to remove user 1, but is not a global owner
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id})
    assert remove_response.status_code == 403

# Remove user and checks if user can still be found
def test_admin_remove_v1_user_list(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id1 = register_response_data1["auth_user_id"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Removes user 2
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id2})

    assert remove_response.status_code == 200

    # List all users
    users_response1 = requests.get(config.url + 'users/all/v1',
                                  params = {'token': token1})

    users_response1 = users_response1.json()
    # User 2 removed
    assert users_response1 == {'users': [{'u_id': auth_user_id1,
            				   	'email': 'testing1@gmail.com',
                                		'name_first': 'First', 
                                		'name_last': 'Test',
							'handle_str': 'firsttest',
                                          'profile_img_url': config.url + "static/default.jpg"}]}

# Checks if removed users is no longer part of channel
# Also checks for channel messages
def test_admin_remove_v1_channel_owner(clear_data):
	# Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id1 = register_response_data1["auth_user_id"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Register user 3
    register_response3 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'yourmum@gmail.com',
                                            'password': 'notthelongestpasswordever',
                                            'name_first': 'Your', 
                                            'name_last': 'Mother'})
    register_response_data3 = register_response3.json()
    token3 = register_response_data3["token"]
    auth_user_id3 = register_response_data3["auth_user_id"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token2,
                                                  "name": "Channel 1",
                                                  "is_public": True})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]	

	# User 1 joins channel
    requests.post(config.url + 'channel/join/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id})

	# User 3 joins channel
    requests.post(config.url + 'channel/join/v2',
                                 json={'token': token3,
                                       'channel_id': channel_id})                                   

	# Make user_1 an owner
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': token2,
                                            'channel_id': channel_id,
                                            'u_id': auth_user_id1})

    # Make user_3 an owner
    requests.post(config.url + 'channel/addowner/v1',
                                    json = {'token': token2,
                                            'channel_id': channel_id,
                                            'u_id': auth_user_id3})

    # User 2 sends a message
    requests.post(config.url + "message/send/v1",
				  json={'token': token2,
						'channel_id': channel_id,
						'message': "HD FOR DAYZ"})

	# Remove user_2
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id2})

    assert remove_response.status_code == 200

	# Check that the channel_details are correct
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token1,
                                          'channel_id': channel_id})

    details_response = details_response.json()
    
    # Make sure details is correct
    assert details_response == {
        'name': 'Channel 1',
        'is_public': True,
        'owner_members': [
            {
				'u_id': auth_user_id1,
				'email': 'testing1@gmail.com',
				'handle_str': 'firsttest',
				'name_first': 'First',
				'name_last': 'Test',
                        'profile_img_url': config.url + "static/default.jpg"
			 },
            {
				'u_id': auth_user_id3,
				'email': 'yourmum@gmail.com',
				'handle_str': 'yourmother',
				'name_first': 'Your',
				'name_last': 'Mother',
                        'profile_img_url': config.url + "static/default.jpg"
			 }
        ],
        'all_members': [
            {
				'u_id': auth_user_id1,
				'email': "testing1@gmail.com",
				'name_first': "First",
				'name_last': "Test",
				'handle_str': "firsttest",
                        'profile_img_url': config.url + "static/default.jpg"
            },
            {
				'u_id': auth_user_id3,
				'email': 'yourmum@gmail.com',
				'handle_str': 'yourmother',
				'name_first': 'Your',
				'name_last': 'Mother',
                        'profile_img_url': config.url + "static/default.jpg"
			 }
        ]
    }
    # Check for 'Removed user' message
    messages_response = requests.get(config.url + "channel/messages/v2",
                                     params={'token': token1,
                                             'channel_id':channel_id,
                                             'start': 0})
    messages_response = messages_response.json()

    assert messages_response['messages'][0]['message_id'] == 1
    assert messages_response['messages'][0]['u_id'] == auth_user_id2
    assert messages_response['messages'][0]['message'] == "Removed user"

# Checks dm_details
def test_admin_remove_v1_dm_details(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id1 = register_response_data1["auth_user_id"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Create dm
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                 json={'token': token2,
                                       'u_ids': [auth_user_id1]})

    dm_create_response = dm_create_response.json()

	# Remove user_2
    requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id2})

    # Get dm details
    details_response = requests.get(config.url + "dm/details/v1",
                               params={'token': token1,
                                       'dm_id': dm_create_response['dm_id']})

    details_response = details_response.json()

    assert details_response == {
        'name': 'derrickdoan, firsttest',
        'members': [{'u_id': 1, 
                     'email': 'testing1@gmail.com',
                     'name_first': 'First',
                     'name_last': 'Test',
                     'handle_str': 'firsttest',
                     'profile_img_url': config.url + "static/default.jpg"}, 
                    ]
        }

# Checks if user is removed from dm, and messages are changed
def test_admin_remove_v1_dm_remove(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id1 = register_response_data1["auth_user_id"]
    
    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    auth_user_id2 = register_response_data2["auth_user_id"]

    # Create dm
    dm_create_response = requests.post(config.url + "dm/create/v1", 
                                 json={'token': token1,
                                       'u_ids': [auth_user_id2]})

    dm_create_response = dm_create_response.json()

    # User2 sends a message
    requests.post(config.url + "message/senddm/v1",
                             json={'token': token2,
                                   'dm_id': dm_create_response['dm_id'],
                                   'message': "Cya later, Alligator"})

    # User1 sends a message
    requests.post(config.url + "message/senddm/v1",
                             json={'token': token1,
                                   'dm_id': dm_create_response['dm_id'],
                                   'message': "Evil programming be like: Goodbye World"})

	# Remove user_2
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id2})

    assert remove_response.status_code == 200

    # Check dm details are correct
    details_response = requests.get(config.url + "dm/details/v1",
                               params={'token': token1,
                                       'dm_id': dm_create_response['dm_id']})

    details_response = details_response.json()

    assert details_response == {
        'name': 'derrickdoan, firsttest',
        'members': [{'u_id': 1, 
                     'email': 'testing1@gmail.com',
                     'name_first': 'First',
                     'name_last': 'Test',
                     'handle_str': 'firsttest',
                     'profile_img_url': config.url + "static/default.jpg"}, 
                    ]
        }

    # Check for correct messages
    dm_message_response = requests.get(config.url + "dm/messages/v1", 
                            params={'token': token1,
                                    'dm_id': dm_create_response['dm_id'],
                                    'start': 0})

    dm_message_response = dm_message_response.json()
    assert dm_message_response['messages'][0]['message_id'] == 2
    assert dm_message_response['messages'][0]['u_id'] == auth_user_id1
    assert dm_message_response['messages'][0]['message'] == "Evil programming be like: Goodbye World"

    assert dm_message_response['messages'][1]['message_id'] == 1
    assert dm_message_response['messages'][1]['u_id'] == auth_user_id2
    assert dm_message_response['messages'][1]['message'] == "Removed user"

# Test whether user profile is still retrievable with users/profile
def test_admin_remove_profile_still_retrievable(clear_data):

    # Register 2 users, the first user will be a global owner
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})

    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User 1 removes user 2
    requests.delete(config.url + 'admin/user/remove/v1',
                    json={'token': register_response1['token'],
                          'u_id': register_response2['auth_user_id']})

    # Check that user 2's profile is still retrievable
    profile_response = requests.get(config.url + 'user/profile/v1',
                                    params={'token': register_response1['token'],
                                            'u_id': register_response2['auth_user_id']})

    assert profile_response.json() == {
                        'user': {
                            'u_id': register_response2['auth_user_id'],
                            'email': "",
                            'name_first': "Removed",
                            'name_last': "user",
                            'handle_str': "",
                            'profile_img_url': ''
                        }
                }

# Test whether removed message do not affect this function
def test_admin_remove_removed_message(clear_data):

    # Register 2 users
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})

    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User 1 creates a channel
    channel = requests.post(config.url + "channels/create/v2",
                            json={"token": register_response1['token'],
                                  "name": "Channel 1",
                                  "is_public": True})
    channel = channel.json()

    # User 2 joins the channel
    requests.post(config.url + "channel/join/v2",
                  json={'token': register_response2['token'],
                        'channel_id': channel['channel_id']})

    # User 2 sends 2 messages
    send_response1 = requests.post(config.url + "message/send/v1",
                                   json={'token': register_response2['token'],
                                    	 'channel_id': channel['channel_id'],
                                         'message': "Hello world"})
    
    send_response1 = send_response1.json() 

    requests.post(config.url + "message/send/v1",
                  json={'token': register_response2['token'],
                        'channel_id': channel['channel_id'],
                        'message': "Hello world"})

    # User 1 removes the first message
    requests.delete(config.url + "message/remove/v1",
                    json={'token': register_response1['token'],
                          'message_id': send_response1['message_id']})

    # User 1 removes user 2
    remove_response = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': register_response1['token'],
                                       'u_id': register_response2['auth_user_id']})

    assert remove_response.status_code == 200

# Test a user cannot be removed twice and InputError status code is returned
def test_admin_remove_cant_remove_twice(clear_data):

    # Register 2 users
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})

    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})

    register_response1 = register_response1.json()
    register_response2 = register_response2.json()

    # User 1 removes user 2
    remove_response1 = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': register_response1['token'],
                                       'u_id': register_response2['auth_user_id']})

    assert remove_response1.status_code == 200

    # User 1 tries to remove user 2 again (user 2's u_id is invalid)
    remove_response2 = requests.delete(config.url + 'admin/user/remove/v1',
                                 json={'token': register_response1['token'],
                                       'u_id': register_response2['auth_user_id']})

    assert remove_response2.status_code == 400


    


                                              