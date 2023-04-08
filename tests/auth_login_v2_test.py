import pytest
import requests
from src import config

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test if no email raises inputerror
def test_login_v2_no_email(clear_data):

    # Login the user given no email
    login_response = requests.post(config.url + "auth/login/v2", 
                        json={"email": "",
                              "password": "validpassword"})

    assert login_response.status_code == 400

# Test if invalid email raises inputerror
def test_login_v2_invalid_email(clear_data):

    # Register user
    requests.post(config.url + "auth/register/v2",
                 json={"email": "justin@gmail.com",
                       "password": "validpassword",
                       "name_first": "Justin",
                       "name_last": "Son"})

    # Log in user with invalid email
    login_response = requests.post(config.url + "auth/login/v2", 
                        json={"email": "justin.gmail.com", 
                              "password": "validpassword"})

    assert login_response.status_code == 400

# Test if email that doesnt belong to any user raises inputerror
def test_login_v2_non_existing_email(clear_data):

    # Register user
    requests.post(config.url + "auth/register/v2",
                 json={"email": "justin@gmail.com",
                       "password": "validpassword",
                       "name_first": "Justin",
                       "name_last": "Son"})

    # Log in user with different email
    login_response = requests.post(config.url + "auth/login/v2", 
                        json={"email": "different@gmail.com", 
                              "password": "differentpassword"})

    assert login_response.status_code == 400

# Test if no password raises inputerror
def test_login_no_password(clear_data):

    # Register user
    requests.post(config.url + "auth/register/v2",
                 json={"email": "justin@gmail.com",
                       "password": "validpassword",
                       "name_first": "Justin",
                       "name_last": "Son"})

    # Log in user with empty password
    login_response = requests.post(config.url + "auth/login/v2",
                                  json={"email": "justin@gmail.com",
                                        "password": ""})

    assert login_response.status_code == 400

# Test if incorrect password raises inputerror
def test_login_incorrect_password(clear_data):
    
    # Register user
    requests.post(config.url + "auth/register/v2",
                 json={"email": "justin@gmail.com",
                       "password": "correctpassword",
                       "name_first": "Justin",
                       "name_last": "Son"})

    # Log user in with incorrect password
    login_response = requests.post(config.url + "auth/login/v2",
                                  json={"email": "justin@gmail.com",
                                        "password": "wrongpassword"})

    assert login_response.status_code == 400

# Test if the login function works
def test_login_works(clear_data):

    # Register user, and get their register id
    register_response = requests.post(config.url + "auth/register/v2",
                                     json={"email": "hyunseo@gmail.com",
                                           "password": "correctpassword",
                                           "name_first": "Justin",
                                           "name_last": "Son"})
    register_response_data = register_response.json()
    register_id = register_response_data['auth_user_id']
    
    # Login user, and get their login id
    login_response = requests.post(config.url + "auth/login/v2",
                                  json={"email": "hyunseo@gmail.com",
                                        "password": "correctpassword"})
    login_response_data = login_response.json()
    login_id = login_response_data['auth_user_id']

    assert register_id == login_id

# Check that a user can have multiple sessions
def test_login_multiple_sessions(clear_data):

    # Register a user
    register_response = requests.post(config.url + "auth/register/v2",
                                     json={"email": "hyunseo@gmail.com",
                                           "password": "correctpassword",
                                           "name_first": "Justin",
                                           "name_last": "Son"})
    register_response = register_response.json()

    # Login the user in a different browser
    login_response = requests.post(config.url + "auth/login/v2",
                                  json={"email": "hyunseo@gmail.com",
                                        "password": "correctpassword"})
    login_response = login_response.json()

    assert register_response['token'] != login_response['token']

    # Check that both tokens work
    create_response1 = requests.post(config.url + "channels/create/v2",
                                    json={'token': register_response['token'],
                                    'name': "Hello",
                                    'is_public': True})

    assert create_response1.status_code == 200

    create_response2 = requests.post(config.url + "channels/create/v2",
                                    json={'token': login_response['token'],
                                    'name': "world",
                                    'is_public': True})

    assert create_response2.status_code == 200

    # Logout the first session
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_response['token']})

    # Check that the first token is no longer valid
    create_response3 = requests.post(config.url + "channels/create/v2",
                                    json={'token': register_response['token'],
                                    'name': "hi",
                                    'is_public': True})

    assert create_response3.status_code == 403

    # Check that the second token is still valid
    create_response4 = requests.post(config.url + "channels/create/v2",
                                    json={'token': login_response['token'],
                                    'name': "water",
                                    'is_public': True})

    assert create_response4.status_code == 200









