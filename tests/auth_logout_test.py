import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
# Test if user token is invalid
def test_logout_invalid_token(clear_data):
    
    logout_response = requests.post(config.url + "auth/logout/v1",
                                    json={"token": invalid_token1()})

    assert logout_response.status_code == 403
    
# Test if user can logout after logging out
def test_logout_after_logout(clear_data):
    
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "hyunseo@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Justin",
                                            "name_last": "Son"})
    register_response_data = register_response.json()
    register_token = register_response_data['token']
    
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_token})
    
    logout_response = requests.post(config.url + "auth/logout/v1",
                                    json={"token": register_token})

    assert logout_response.status_code == 403

# Test if user can log out after registering
def test_logout_after_register(clear_data):

    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "hyunseo@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Justin",
                                            "name_last": "Son"})
    register_response_data = register_response.json()
    register_token = register_response_data['token']
    
    logout_response = requests.post(config.url + "auth/logout/v1",
                                    json={"token": register_token})

    assert logout_response.status_code == 200
    
# Test if multiple users can login and log out
def test_logout_multiple_users(clear_data):
    
    # Register user 1
    register_response1 = requests.post(config.url + "auth/register/v2",
                                      json={"email": "hyunseo@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Justin",
                                            "name_last": "Son"})
    register_response_data1 = register_response1.json()
    token1 = register_response_data1['token']
    
    # Register user 2
    register_response2 = requests.post(config.url + "auth/register/v2",
                                      json={"email": "cynthia@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "cynthia",
                                            "name_last": "li"})
    register_response_data2 = register_response2.json()
    token2 = register_response_data2['token']
    
    # Register user 3
    register_response3 = requests.post(config.url + "auth/register/v2",
                                      json={"email": "derrick@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Derrick",
                                            "name_last": "Doan"})
    register_response_data3 = register_response3.json()
    token3 = register_response_data3['token']

    # Log user 1 and 2 out
    assert requests.post(config.url + "auth/logout/v1",
                  json={"token": token1})
    
    assert requests.post(config.url + "auth/logout/v1",
                  json={"token": token2})
    
    # Send get request for all channels the user is in
    list_response1 = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token1})

    list_response2 = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token2})

    list_response3 = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token3})
    
    assert list_response1.status_code == 403
    assert list_response2.status_code == 403
    assert list_response3.status_code == 200
    
# Test if user can register, logout and log back in
def test_logout_after_registerd_then_login(clear_data):

    # Register user 1
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "hyunseo@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Justin",
                                            "name_last": "Son"})
    register_response_data = register_response.json()
    token = register_response_data['token']
    
    # Log user 1 out
    assert requests.post(config.url + "auth/logout/v1",
                  json={"token": token})
    
    # Log in user again
    login_response = requests.post(config.url + "auth/login/v2", 
                        json={"email": "hyunseo@gmail.com",
                              "password": "validpassword123"})
    login_response_data = login_response.json()
    token = login_response_data['token']
    
    # Send get request for all channels the user is in
    list_response = requests.get(config.url + "channels/listall/v2",
                                 params={'token': token})
    
    assert list_response.status_code == 200
    