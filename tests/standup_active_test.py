import pytest
import requests
import datetime
import time 
from src import config
from src.error import AccessError, InputError, Success
from tests.test_helpers import invalid_token1, request_register, \
                               request_channels_create, request_start_standup, \
                               request_active_standup 

@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


# token not valid
def test_standup_active_user_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    active_response = request_active_standup(invalid_token1(), channel_id)

    assert active_response.status_code == AccessError.code

#  channel id not valid
def test_standup_active_channel_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    active_response = request_active_standup(token, -1)

    assert active_response.status_code == InputError.code

# channel id valid but user is not part of channel 
def test_standup_active_not_member(clear_data):
    user1 = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token1 = user1["token"]

    user2 = request_register("chopin@gmail.com", "password1", "frederic", "chopin").json()
    token2 = user2["token"]

    channel = request_channels_create(token1, "Channel1", True).json()
    channel_id = channel["channel_id"]

    active_response = request_active_standup(token2, channel_id)

    assert active_response.status_code == AccessError.code

# Test when no active standup
def test_standup_active_return_false(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    active_response = request_active_standup(token, channel_id).json()

    assert active_response == {'is_active': False,
                               'time_finish': None}

# Test for the correct return, inlcuding times
def test_standup_active_return_type(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    start_response = request_start_standup(token, channel_id, 2).json()

    active_response = request_active_standup(token, channel_id).json()

    assert active_response == {'is_active': True,
                               'time_finish': start_response['time_finish']}
 
# Test for multiple channels
def test_standup_active_multiple(clear_data):
    user1 = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token1 = user1["token"]

    user2 = request_register("chopin@gmail.com", "password1", "frederic", "chopin").json()
    token2 = user2["token"]

    channel1 = request_channels_create(token1, "Channel1", True).json()
    channel_id1 = channel1["channel_id"]

    channel2 = request_channels_create(token2, "Channel2", True).json()
    channel_id2 = channel2["channel_id"]

    start_response1 = request_start_standup(token1, channel_id1, 2).json()

    start_response2 = request_start_standup(token2, channel_id2, 1).json()

    active_response1 = request_active_standup(token1, channel_id1).json()

    active_response2 = request_active_standup(token2, channel_id2).json()

    assert active_response1 == {'is_active': True,
                               'time_finish': start_response1['time_finish']}

    assert active_response2 == {'is_active': True,
                               'time_finish': start_response2['time_finish']}

