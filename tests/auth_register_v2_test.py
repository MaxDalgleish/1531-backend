import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError, Success
from .test_helpers import request_register, request_channels_create, \
                          request_channel_details, request_channel_join, \
                          request_login

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")

# Helper function that searchs for the user with the given auth_user_id
def search_user(auth_user_id, users):

    # Loop through all users
    for user in users:
        # If a matching auth user id is found return user
        if user["u_id"] is auth_user_id:
            return user

# Test if inputerror is raised if no email is given
def test_register_v2_email_none(clear_data):

    # Register user
    register_response = request_register("",
                                         "validpassword123",
                                         "Justin",
                                         "Son")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised if invalid email is given
def test_register_v2_email_invalid(clear_data):

    # Register user
    register_response = request_register("invalid.email.student.unsw.edu.au",
                                         "validpassword123",
                                         "Justin",
                                         "Son")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised if the email is a duplicate
def test_register_v2_email_duplicate(clear_data):

    # Register user 1
    request_register("justin@gmail.com",
                     "validpassword123",
                     "Justin",
                     "Son")

    # Register user 2 with same email
    register_response2 = request_register("justin@gmail.com",
                                          "validpassword123",
                                          "Justin",
                                          "Son")

    assert register_response2.status_code == InputError.code

# Test if inputerror is raised if the password was not entered
def test_register_v2_password_none(clear_data):
    
    # Register user
    register_response = request_register("justin@gmail.com",
                                          "",
                                          "Justin",
                                          "Son")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised if the password is less than 6 characters
def test_register_v2_password_length_invalid(clear_data):

    # Register user
    register_response = request_register("justin@gmail.com",
                                          "12345",
                                          "Justin",
                                          "Son")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised when first name length is less than 1 character
# (i.e empty)
def test_register_v2_first_name_too_short(clear_data):

    # Register user
    register_response = request_register("justin@gmail.com",
                                          "validpassword123",
                                          "",
                                          "Son")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised if the length of first name is more than 50 characters
def test_register_v2_first_name_too_long(clear_data):
    
    # Register user
    register_response = request_register("testing@gmail.com",
                                         "validpassword123",
                                         "Henricheyvindrfaustakarissaklavdiyasumatiainamilkaalyson",
                                         "King")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised when last name length is less than 1 character
# (i.e empty)
def test_register_v2_last_name_too_short(clear_data):

    # Register user
    register_response = request_register("justin@gmail.com",
                                         "12345",
                                         "Justin",
                                         "")

    assert register_response.status_code == InputError.code

# Test if inputerror is raised if the length of last name is more than 50 characters
def test_register_v2_last_name_too_long(clear_data):

    # Register user
    register_response = request_register("testing@gmail.com",
                                         "validpassword123",
                                         "Henry",
                                         "Wolfe­schlegel­stein­hausen­berger­dorffavielteoinyenepersephone")

    assert register_response.status_code == InputError.code

# Test if the concatenated handle only consists of lowercase alphanumeric first
# and last name
def test_register_v2_concatenated_handle_valid(clear_data):

    # Register user, and get their user id and token
    register_response = request_register("justinnn@gmail.com",
                                         "validpassword123",
                                         "Justin",
                                         "Son")
    register_response_data = register_response.json()
    auth_user_id = register_response_data["auth_user_id"]
    token = register_response_data["token"]

    # Create channel and get channel id
    channel_create_response = request_channels_create(token,
                                                      "Channel_1",
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # Get channel details and find owner members
    channel_details_response = request_channel_details(token,
                                                       channel_id)
    channel_details_response_data = channel_details_response.json()
    owner_members = channel_details_response_data['owner_members']
    
    # Find the owner's handle from the list
    found_owner = search_user(auth_user_id, owner_members)
    handle = found_owner["handle_str"]

    assert handle == "justinson"

# Test if concatenated handle is cut off at 20 characters
def test_register_v2_concatenated_handle_length(clear_data):

    # Register user and get their auth_user_id and token
    register_response = request_register("Kamala@gmail.com",
                                         "validpassword123",
                                         "Kamalaneta",
                                         "Calogerusilips")
    register_response_data = register_response.json()
    auth_user_id = register_response_data["auth_user_id"]
    token = register_response_data["token"]

    # Create channel and get channel id
    channel_create_response = request_channels_create(token,
                                                      "Channel_1",
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # Find channel details and get list of owner members
    channel_details_response = request_channel_details(token,
                                                       channel_id)
    channel_details_response_data = channel_details_response.json()
    owner_members = channel_details_response_data["owner_members"]
    
    # Find the owner's handle from the list
    found_owner = search_user(auth_user_id, owner_members)
    handle = found_owner["handle_str"]

    assert len(handle) == 20
    assert handle == "kamalanetacalogerusi"

# Test if new handle with 0 appended to the end is created once the handle is
# taken again
def test_register_concatenated_handle_append(clear_data):

    # Register user 1 and get their auth_user_id and token
    register_response1 = request_register("Kamala@gmail.com",
                                          "validpassword123",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data1 = register_response1.json()
    auth_user_id1 = register_response_data1["auth_user_id"]
    token1 = register_response_data1["token"]

    # Register user 2 and get their auth_user_id and token
    register_response2 = request_register("Kamala.Cal@gmail.com",
                                          "differentpassword123",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data2 = register_response2.json()
    auth_user_id2 = register_response_data2["auth_user_id"]
    token2 = register_response_data2["token"]

    # Create channel and get channel id
    channel_create_response = request_channels_create(token1,
                                                      "Channel_1",
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # User 2 joins the channel created by user 1
    request_channel_join(token2,
                         channel_id)

    # Find channel details and get list of all members
    channel_details_response = request_channel_details(token1,
                                                       channel_id)
    channel_details_response_data = channel_details_response.json()
    all_members = channel_details_response_data["all_members"]
    
    # Find the members from the list
    found_member1 = search_user(auth_user_id1, all_members)
    found_member2 = search_user(auth_user_id2, all_members)

    assert found_member2["handle_str"] == found_member1["handle_str"] + str(0)

# Test if the handle returned for multiple people with the same name has index
# appended
def test_register_concatenated_handle_duplicate(clear_data):

    # Register user 1 and get their auth_user_id and token
    register_response1 = request_register("Kamala@gmail.com",
                                          "validpassword1",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data1 = register_response1.json()
    auth_user_id1 = register_response_data1["auth_user_id"]
    token1 = register_response_data1["token"]

    # Register user 2 and get their auth_user_id and token
    register_response2 = request_register("Kamala.C@gmail.com",
                                          "validpassword2",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data2 = register_response2.json()
    auth_user_id2 = register_response_data2["auth_user_id"]
    token2 = register_response_data2["token"]

    # Register user 3 and get their auth_user_id and token
    register_response3 = request_register("Kamala.Cal@gmail.com",
                                          "validpassword3",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data3 = register_response3.json()
    auth_user_id3 = register_response_data3["auth_user_id"]
    token3 = register_response_data3["token"]

    # Register user 4 and get their auth_user_id and token
    register_response4 = request_register("Kamala.Cal0@gmail.com",
                                          "validpassword4",
                                          "Kamalaneta",
                                          "Calogerusilips")
    register_response_data4 = register_response4.json()
    auth_user_id4 = register_response_data4["auth_user_id"]
    token4 = register_response_data4["token"]

    # Create channel and get channel id
    channel_create_response = request_channels_create(token1,
                                                      "Channel_1",
                                                      True)
    channel_create_response_data = channel_create_response.json()
    channel_id = channel_create_response_data["channel_id"]

    # Users 2 3 and 4 joins the channel created by user 1
    request_channel_join(token2,
                         channel_id)
    request_channel_join(token3,
                         channel_id)
    request_channel_join(token4,
                         channel_id)

    # Find channel details and get list of all members
    channel_details_response = request_channel_details(token1,
                                                       channel_id)
    channel_details_response_data = channel_details_response.json()
    all_members = channel_details_response_data["all_members"]
    
    # Find the users from the list of all members
    found_member1 = search_user(auth_user_id1, all_members)
    found_member2 = search_user(auth_user_id2, all_members)
    found_member3 = search_user(auth_user_id3, all_members)
    found_member4 = search_user(auth_user_id4, all_members)

    assert found_member1["handle_str"] == "kamalanetacalogerusi"
    assert found_member2["handle_str"] == "kamalanetacalogerusi0"
    assert found_member3["handle_str"] == "kamalanetacalogerusi1"
    assert found_member4["handle_str"] == "kamalanetacalogerusi2"

# Test if the auth register function works
def test_register_works(clear_data):

    # Register user, and get their register id
    register_response = request_register("justin@gmail.com",
                                         "correctpassword",
                                         "Justin",
                                         "Son")
    register_response_data = register_response.json()
    register_id = register_response_data['auth_user_id']

    # Login user, and get their login id
    login_response = request_login("justin@gmail.com",
                                   "correctpassword")
    login_response_data = login_response.json()
    login_id = login_response_data['auth_user_id']

    assert register_id == login_id

# Test if InputError is raised when name_first and name_last both do not include
# any alphanumeric chars
def test_no_alphanumeric(clear_data):

    # Register user
    register_response = request_register("justin@gmail.com",
                                         "correctpassword",
                                         "$%#&@*@(*&",
                                         "#$%@^@%$&*")

    assert register_response.status_code == InputError.code
