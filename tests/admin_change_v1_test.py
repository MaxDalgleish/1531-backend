import pytest
import requests 
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Invalid token
def test_admin_change_v1_invalid_token(clear_data):

    # Register user 1
    requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})

	# Invalid token passed in
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': invalid_token1(),
                                       'u_id': '1',
                                       'permission_id': 1})
    assert change_response.status_code == 403


# U_id does not refer to a valid user
def test_admin_change_v1_invalid_user(clear_data):

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

	# Change user but has wrong u_id
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id + 1,
                                       'permission_id': 1})
    assert change_response.status_code == 400

# U_id refers to a user who is the only global owner and they are being demoted to a user
def test_admin_change_v1_only_global_owner(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    auth_user_id = register_response_data1["auth_user_id"]

	# User 1 tries to demote themselves
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id,
                                       'permission_id': 2})

    assert change_response.status_code == 400

# Permission_id is invalid
def test_admin_change_v1_invalid_permission_id(clear_data):
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

	# Permission invalid, not 1 or 2
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id,
                                       'permission_id': 3})
    assert change_response.status_code == 400

# The authorised user is not a global owner
def test_admin_change_v1_not_global_owner(clear_data):
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

	# User 2 not a global owner
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id,
                                       'permission_id': 2})
    assert change_response.status_code == 403

# Testing for multiple global owners demoting themselves
# Also tests for correct return
def test_admin_change_v1_correct_demotion(clear_data):
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

	# User 1 makes user 2 global owner
    change_response1 = requests.post(config.url + 'admin/userpermission/change/v1',
									json={'token': token1,
										'u_id': auth_user_id2,
										'permission_id': 2})

    assert change_response1.status_code == 200

    change_response1 = change_response1.json()
    assert change_response1 == {}

	# User 2 demotes themselves
    change_response2 = requests.post(config.url + 'admin/userpermission/change/v1',
									json={'token': token2,
										'u_id': auth_user_id2,
										'permission_id': 2})

    assert change_response2.status_code == 200		
				
	# User 1 demotes themselves, but fails
    change_response3 = requests.post(config.url + 'admin/userpermission/change/v1',
									json={'token': token1,
										'u_id': auth_user_id1,
										'permission_id': 2})

    assert change_response3.status_code == 400	



# Test for correct change by checking if they can join a channel
def test_admin_change_v1_correct_joining(clear_data):
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
    token2 = register_response_data2["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token1,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

	# User 2 joins channel, bit fails as it is private
    join_response1 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                       'channel_id': channel_id})

    assert join_response1.status_code == 403
	
	# Change user to global owner
    change_response = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': auth_user_id,
                                       'permission_id': 1})

    assert change_response.status_code == 200

	# User 2 can now join channel
    join_response2 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                 	   'channel_id': channel_id})

    assert join_response2.status_code == 200                                          

# Another test for correct behaviour for correct joining
def test_admin_change_v1_correct_joining2(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    u_id1 = register_response_data1["auth_user_id"]

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    u_id2 = register_response_data2["auth_user_id"]

	# Register user 3
    register_response3 = requests.post(config.url + 'auth/register/v2', 
                     json={'email': 'panda@gmail.com',
                           'password': 'panda12345',
                           'name_first': 'panda', 
                           'name_last': 'bear'})
    register_response_data3 = register_response3.json()
    token3 = register_response_data3["token"]

    # Create channel and get channel id
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token3,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # User_1 changes user_2 to global owner
    change_response1 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': u_id2,
                                       'permission_id': 1})
    assert change_response1.status_code == 200

    # User_2 demotes user_1
    change_response2 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token2,
                                       'u_id': u_id1,
                                       'permission_id': 2})
    assert change_response2.status_code == 200

    # User_1 joins the channel, but is unsuccessful
    join_response1 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id})

    assert join_response1.status_code == 403

    # User_2 joins the channel and is successful
    join_response2 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                      'channel_id': channel_id})

    assert join_response2.status_code == 200


# Test for correct behaviour for multiple users
def test_admin_change_v1_multiple_users(clear_data):
    # Register user 1
    register_response1 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'testing1@gmail.com',
                                            'password': 'validpassword',
                                            'name_first': 'First', 
                                            'name_last': 'Test'})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1["token"]
    u_id1 = register_response_data1["auth_user_id"]

    # Register user 2
    register_response2 = requests.post(config.url + 'auth/register/v2', 
                                      json={'email': 'derrick@gmail.com',
                                            'password': 'validpassword1',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2["token"]
    u_id2 = register_response_data2["auth_user_id"]

    # Register user 3
    register_response3 = requests.post(config.url + 'auth/register/v2', 
                     json={'email': 'panda@gmail.com',
                           'password': 'panda12345',
                           'name_first': 'panda', 
                           'name_last': 'bear'})
    register_response_data3 = register_response3.json()
    token3 = register_response_data3["token"]
    u_id3 = register_response_data3["auth_user_id"]

    # User_1 changes user_2, his best friend, to global owner
    change_response1 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': u_id2,
                                       'permission_id': 1})
    assert change_response1.status_code == 200

    # User_2 changes his other friend user_3 to global owner
    change_response2 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token2,
                                       'u_id': u_id3,
                                       'permission_id': 1})
    assert change_response2.status_code == 200

    # User_1 decided the pressure as a global owner was too much, and steps down.
    # User_1 changes himself to a regular member
    change_response3 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token1,
                                       'u_id': u_id1,
                                       'permission_id': 2})
    assert change_response3.status_code == 200

    # User_3 betrays user_2 and makes him a regular member
    change_response4 = requests.post(config.url + 'admin/userpermission/change/v1',
                                 json={'token': token3,
                                       'u_id': u_id2,
                                       'permission_id': 2})
    assert change_response4.status_code == 200

    # Register user 4
    register_response4 = requests.post(config.url + 'auth/register/v2', 
                     json={'email': 'koala@gmail.com',
                           'password': 'koala12345',
                           'name_first': 'koala', 
                           'name_last': 'koala'})
    register_response_data4 = register_response4.json()
    token4 = register_response_data4["token"]
    u_id4 = register_response_data4["auth_user_id"]

    # User 4 creates a private channel
    channel_create_response = requests.post(config.url + "channels/create/v2",
                                            json={"token": token4,
                                                  "name": "Channel 1",
                                                  "is_public": False})
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # User_1 joins the channel, but is unsuccessful
    join_response1 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token1,
                                       'channel_id': channel_id})

    assert join_response1.status_code == 403

    # User_2 joins the channel and is also unsuccessful
    join_response2 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token2,
                                       'channel_id': channel_id})

    assert join_response2.status_code == 403

    # User_3 joins the channel and is successful
    join_response3 = requests.post(config.url + 'channel/join/v2',
                                 json={'token': token3,
                                       'channel_id': channel_id})

    assert join_response3.status_code == 200

    # Check that the channel_details are correct
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token4,
                                          'channel_id': channel_id})

    details_response = details_response.json()
    
    # Make sure details is correct
    assert details_response == {
        'name': 'Channel 1',
        'is_public': False,
        'owner_members': [
            {
                'u_id': u_id4,
                'email': "koala@gmail.com",
                'name_first': "koala",
                'name_last': "koala",
                'handle_str': "koalakoala",
                'profile_img_url': config.url + "static/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': u_id4,
                'email': "koala@gmail.com",
                'name_first': "koala",
                'name_last': "koala",
                'handle_str': "koalakoala",
                'profile_img_url': config.url + "static/default.jpg"
            },
            {
                'u_id': u_id3,
                'email': "panda@gmail.com",
                'name_first': "panda",
                'name_last': "bear",
                'handle_str': "pandabear",
                'profile_img_url': config.url + "static/default.jpg"
            }
        ]
    }
