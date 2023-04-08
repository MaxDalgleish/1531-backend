import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1, invalid_token2

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

# Testing invalid user token returning AccessError Code
def test_user_profile_v1_invalid_token(clear):
    
    requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    user_response = requests.get(config.url + "user/profile/v1",
                                  params={"token": invalid_token1(), "u_id": 1})

    assert user_response.status_code == 403

# Testing with invalid u_id returning InputError Code 
def test_user_profile_v1_invalid_uid(clear):
    
    reg_response = create_user1()
 
    user_response = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response["token"], "u_id": 999})

    assert user_response.status_code == 400

# Testing invalid user token and invalid u_id and returning AccessError Code
def test_user_profile_v1_invalid_input(clear):
    
    requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    user_response = requests.get(config.url + "user/profile/v1",
                                  params={"token": invalid_token2(), "u_id": 100000})

    assert user_response.status_code == 403

# Testing with one user created
def test_user_profile_v1_one_user(clear):
    
    reg_response = create_user1()
 
    user_response = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response["token"], 
                                  "u_id": reg_response["auth_user_id"]})

    assert user_response.json() == {'user': user1_info()}

# Testing with two users created and requesting their own user profile and the other users'
def test_user_profile_v1_two_users(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()

    user_response1 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response1["token"], "u_id": 1})
    
    user_response2 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response2["token"], "u_id": 2})
    
    user_response3 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response1["token"], "u_id": 2})

    user_response4 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response2["token"], "u_id": 1})

    assert user_response1.json() == {'user': user1_info()}
    assert user_response2.json() == {'user': user2_info()}
    assert user_response3.json() == {'user': user2_info()}
    assert user_response4.json() == {'user': user1_info()}
                            
# Testing with three users created and request themselves' and other users' profile data
def test_user_profile_v1_three_users(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    user_response1 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response1["token"], "u_id": 1})

    user_response2 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response2["token"], "u_id": 2})

    user_response3 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response3["token"], "u_id": 3})

    user_response4 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response1["token"], "u_id": 2})
    
    user_response5 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response2["token"], "u_id": 3})
    
    user_response6 = requests.get(config.url + "user/profile/v1",
                                  params={"token": reg_response3["token"], "u_id": 1})

    assert user_response1.json() == {'user': user1_info()}
    assert user_response2.json() == {'user': user2_info()}
    assert user_response3.json() == {'user': user3_info()}
    assert user_response4.json() == {'user': user2_info()}
    assert user_response5.json() == {'user': user3_info()}
    assert user_response6.json() == {'user': user1_info()}
    

 