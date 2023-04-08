import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Registering user one
def create_user1():

    # Register a user
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    return reg_response.json()

# User 1 return info
def user1_info():
    return{"u_id": 1,
            "email": "test1@gmail.com",
            "name_first": "John",
            "name_last": "Doe",
            "handle_str": "johndoe",
            'profile_img_url': config.url + "static/default.jpg"
            }

# Registering user two
def create_user2():

    # Register a user
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test2@gmail.com',
                        'password': 'validresponse',
                        'name_first': 'Pikachu', 
                        'name_last': 'Ash'})

    return reg_response.json()

# User 2 return info
def user2_info():
    return {"u_id": 2,
            "email": "test2@gmail.com",
            "name_first": "Pikachu",
            "name_last": "Ash",
            "handle_str": "pikachuash",
            'profile_img_url': config.url + "static/default.jpg"
            }

# Registering user three
def create_user3():

    # Register a user
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test3@gmail.com',
                        'password': 'testing',
                        'name_first': 'Good', 
                        'name_last': 'Day'})

    return reg_response.json()

# User 3 return info
def user3_info():
    return {"u_id": 3,
            "email": "test3@gmail.com",
            "name_first": "Good",
            "name_last": "Day",
            "handle_str": "goodday",
            'profile_img_url': config.url + "static/default.jpg"
            }

######################################### TESTING BEGINS #########################################

# Testing invalid user token
def test_users_all_v1_invalid_token(clear):
    
    requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    users_response = requests.get(config.url + "users/all/v1",
                                  params={"token": invalid_token1()})

    assert users_response.status_code == 403

# Testing with one user created
def test_users_all_v1_one_user(clear):
    
    reg_response = create_user1()
 
    users_response = requests.get(config.url + "users/all/v1",
                                  params={"token": reg_response["token"]})

    users_response = users_response.json()

    user1 = user1_info()

    assert users_response == {"users": [user1]}

# Testing with two users created
def test_users_all_v1_two_users(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()

    users_response1 = requests.get(config.url + "users/all/v1",

                                  params={"token": reg_response1["token"]})
    
    users_response1 = users_response1.json()

    users_response2 = requests.get(config.url + "users/all/v1",

                                  params={"token": reg_response2["token"]})

    users_response2 = users_response2.json()

    user1 = user1_info()
    user2 = user2_info()

    assert users_response1 == {"users": [user1,user2]}
    assert users_response2 == {"users": [user1,user2]}
                            
# Testing with three users created
def test_users_all_v1_three_users(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    users_response1 = requests.get(config.url + "users/all/v1",
                                  params={"token": reg_response1["token"]})

    users_response1 = users_response1.json()

    users_response2 = requests.get(config.url + "users/all/v1",
                                  params={"token": reg_response2["token"]})

    users_response2 = users_response2.json()

    users_response3 = requests.get(config.url + "users/all/v1",
                                  params={"token": reg_response3["token"]})

    users_response3 = users_response3.json()

    user1 = user1_info()
    user2 = user2_info()
    user3 = user3_info()

    assert users_response1 == {"users": [user1,user2,user3]}
    assert users_response2 == {"users": [user1,user2,user3]}
    assert users_response3 == {"users": [user1,user2,user3]}
 