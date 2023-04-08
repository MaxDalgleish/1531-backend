import pytest
import requests 
from src import config
from .test_helpers import request_register, passwordreset_request

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')

# Test if inputerror is raised if new password is less than 6 characters long
def test_auth_password_reset_length_invalid(clear_data):
    
    # Register user 1
    register_response1 = request_register('testing@gmail.com',
                                          'validpassword',
                                          'Justin',
                                          'Son')
    register_response1 = register_response1.json()

    # Sending the password reset email
    passwordreset_request('testing@gmail.com')

    # Enter password that is less than 6 characters long
    password_reset_response = requests.post(config.url + 'auth/passwordreset/reset/v1',
                                            json={'reset_code': 123456,
                                                  'new_password': 'newpw'})
    
    assert password_reset_response.status_code == 400

# Test if inputerror is raised if the reset_code_is_invalid
def test_invalid_reset_code(clear_data):
    
    # Register user 1
    register_response1 = request_register('testing@gmail.com',
                                          'validpassword',
                                          'Justin',
                                          'Son')
    register_response1 = register_response1.json()

    # Sending the password reset email
    passwordreset_request('testing@gmail.com')

    # Enter password that is less than 6 characters long
    password_reset_response = requests.post(config.url + 'auth/passwordreset/reset/v1',
                                            json={'reset_code': 123456,
                                                  'new_password': 'newpassword'})
    
    assert password_reset_response.status_code == 400
