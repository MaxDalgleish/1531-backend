import pytest
import requests 
from src import config
from .test_helpers import request_register, request_login, \
                          request_channels_create, passwordreset_request

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Testing if the user is logged out of all sessions
def test_auth_password_reset_logout_all_sessions(clear_data):
    
    # Register user 1
    register_response = request_register('son020120@gmail.com', 
                                         'validpassword',
                                         'Justin',
                                         'Son')
    register_response = register_response.json()
    token = register_response['token']

    # Log user in for a second time
    login_response1 = request_login("son020120@gmail.com",
                                    "validpassword")
    login_response1 = login_response1.json()
    login_token1 = login_response1['token']

    # Log user in for a third time
    login_response2 = request_login("son020120@gmail.com",
                                    "validpassword")
    login_response2 = login_response2.json()
    login_token2 = login_response2['token']

    # Request a password reset email be sent
    passwordreset_request('son020120@gmail.com')
    
    # After the reset request, user attempts to create a channel
    channel_create_response1 = request_channels_create(token,
                                                       'Validchannelone',
                                                       True)
    channel_create_response2 = request_channels_create(login_token1,
                                                       'Validchannelone',
                                                       True)
    channel_create_response3 = request_channels_create(login_token2,
                                                       'Validchannelone',
                                                       True)
    
    assert channel_create_response1.status_code == 403
    assert channel_create_response2.status_code == 403
    assert channel_create_response3.status_code == 403