import pytest
import requests
import datetime
import time 
from src import config
from src.error import AccessError, InputError, Success
from tests.test_helpers import invalid_token1, request_register, \
                               request_channels_create, request_start_standup 

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


# Test for invalid tokens
def test_standup_start_user_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    start_response = request_start_standup(invalid_token1(), channel_id, 1)

    assert start_response.status_code == AccessError.code

# Test for invalid channel_id
def test_standup_start_channel_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    start_response = request_start_standup(token, -2, 1)

    assert start_response.status_code == InputError.code

# Test for negative time lengths
def test_standup_start_negative_length(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    start_response = request_start_standup(token, channel_id, -1)

    assert start_response.status_code == InputError.code

# Test that a startup cannot be started if one is already active
def test_standup_start_active_standup(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    request_start_standup(token, channel_id, 2)
    start_response = request_start_standup(token, channel_id, 1)

    assert start_response.status_code == InputError.code

# Test if the member is not part of the channel, but starting a standup
def test_standup_start_not_member(clear_data):
    user1 = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token1 = user1["token"]

    user2 = request_register("chopin@gmail.com", "password1", "frederic", "chopin").json()
    token2 = user2["token"]

    channel = request_channels_create(token1, "Channel1", True).json()
    channel_id = channel["channel_id"]

    start_response = request_start_standup(token2, channel_id, 1)

    assert start_response.status_code == AccessError.code

# Test that a new standup can be started after the first one finished 
def test_standup_start_end_consecutive(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    request_start_standup(token, channel_id, 1)
    time.sleep(2)

    start_response = request_start_standup(token, channel_id, 1)
    
    assert start_response.status_code == Success.code

# Test that the time returned is correct (within a certain time limit)
def test_standup_start_correct_time(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    start_response = request_start_standup(token, channel_id, 1).json()
    start_response = start_response["time_finish"]

    time_message1 = datetime.datetime.now()
    time_message1 = int(time.mktime(time_message1.timetuple()))

    time_finish = time_message1 + 2
    
    assert abs(start_response - time_finish) < 2

# Test for multiple channels and users
def test_standup_start_multiple(clear_data):
    user1 = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token1 = user1["token"]

    user2 = request_register("chopin@gmail.com", "password1", "frederic", "chopin").json()
    token2 = user2["token"]

    channel1 = request_channels_create(token1, "Channel1", True).json()
    channel_id1 = channel1["channel_id"]

    channel2 = request_channels_create(token2, "Channel2", True).json()
    channel_id2 = channel2["channel_id"]

    start_response1 = request_start_standup(token1, channel_id1, 2)
    assert start_response1.status_code == Success.code

    start_response2 = request_start_standup(token2, channel_id2, 1)
    assert start_response2.status_code == Success.code
