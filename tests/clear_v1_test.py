import pytest
import requests
import json 
from src import config

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Test if the clear function deletes all data and return an empty dictionary
def test_clear_return():

    # Register a user
    requests.post(config.url + "auth/register/v2",
                  json={"email": "max@gmail.com",
                        "password": "reinforcerainstorm",
                        "name_first": "Max",
                        "name_last": "Dalgeish"})

    response = requests.delete(config.url + "clear/v1")
    response_data = response.json()

    # Check clear_v1 response is {}
    assert response_data == {}

# Test whether a user can re-register with the same details once clear_v1 has
# been run and the ids returned are the same
def test_clear_register_user_again(clear_data):

    # Register a user and save their auth_user_id
    old_response = requests.post(config.url + "auth/register/v2",
                                 json={"email": "max@gmail.com",
                                       "password": "reinforcerainstorm",
                                       "name_first": "Max",
                                       "name_last": "Dalgeish"})
    old_response_data = old_response.json()
    old_auth_id = old_response_data['auth_user_id']

    # Clear storage
    requests.delete(config.url + "clear/v1")

    # Register a new user and save their auth_user_id
    new_response = requests.post(config.url + "auth/register/v2",
                                json = {"email": "max@gmail.com",
                                        "password": "reinforcerainstorm",
                                        "name_first": "Max",
                                        "name_last": "Dalgeish"})
    new_response_data = new_response.json()
    new_auth_id = new_response_data['auth_user_id']

    assert old_auth_id == new_auth_id

# Test whether a channel can be recreated with the same details once clear_v1
# has been run and returns the same channel_id
def test_clear_recreate_channel(clear_data):

    # Get response from registering a user
    old_register_response = requests.post(config.url + "auth/register/v2", 
                                          json={"email": "derrick@gmail.com",
                                                "password": "reinforcerainstorm",
                                                "name_first": "Derrick",
                                                "name_last": "Doan"})
    old_register_response_data = old_register_response.json()
    old_auth_id = old_register_response_data['auth_user_id']
    
    # Get response from creating a channel
    old_create_response = requests.post(config.url + "channels/create/v2", 
                                        json={"token": old_register_response_data['token'],
                                              "name": "CamelGroup",
                                              "is_public": False})
    old_create_response_data = old_create_response.json()

    # Clear server
    requests.delete(config.url + "clear/v1")

    # Register the same user again 
    new_register_response = requests.post(config.url + "auth/register/v2", 
                                          json={"email": "derrick@gmail.com",
                                                "password": "reinforcerainstorm",
                                                "name_first": "Derrick", 
                                                "name_last": "Doan"})
    new_register_response_data = new_register_response.json()
    new_auth_id = new_register_response_data['auth_user_id']

    # Get response from creating a new channel
    new_create_response = requests.post(config.url + "channels/create/v2",
                                        json={"token": new_register_response_data['token'],
                                              "name": "CamelGroup",
                                              "is_public": False})
    new_create_response_data = new_create_response.json()

    # Check same response is given
    assert old_create_response_data == new_create_response_data
    assert old_auth_id == new_auth_id
