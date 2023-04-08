import pytest
import requests
import datetime
import time 
from src import config
from src.error import AccessError, InputError, Success
from tests.test_helpers import invalid_token1, request_register, \
                               request_channels_create, get_channel_messages,\
                               request_start_standup, request_send_standup
                               
@pytest.fixture
def clear_data():
    requests.delete(config.url + 'clear/v1')


# token not valid
def test_standup_send_user_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    send_response = request_send_standup(invalid_token1(), channel_id, "Hi")

    assert send_response.status_code == AccessError.code

# Channel id invalid
def test_standup_send_channel_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    send_response = request_send_standup(token, -1, "Hi")

    assert send_response.status_code == InputError.code

# Message > 1000 chars
def test_standup_send_message_length_invalid(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    message = "actckEqlyHRI4G33sJY4PN4RgvAYPecnVJ9TDpG3hu2IMnjDdTU5i2Cm8nzovB7cqQm9ChMKyiGaas1c007bom2BTLIhDGQwTKPgAktTgYSy52IiryPL2WAtaJSqHZuE2cSzxgC6LZPgcXjJt9sBbefAbzX7kgMGBEanvmUgma0kkjue1JJywVgCX8daV5NMoozgZ8j2o5M2a19OdMLdyMxciUvKbi4LUmbjUs61MkPnMICgeIyDWSWsr7jU6PLlNAWXVM58nycpXSRaJSvuExAJbAUBPC3k6Yh8BZImW68v09vQA6gnwFVmzwMvCraqygzysrDLstKLREZrjcopFMYdRiq3zM2p59uxp8X3p44FXsQTQ1Ptu1AkJu4g8TRB6j1YQ5QXZyUZfx0xPdgrVqh6UzpIB9aegVJMBojvx1iXlGJ9HQ6JqC6maTC9NeuESYtDfzLImczY4fXUgg8sXaTzhTGs3LrFeiDJBML3iErkDMRrLJCuVl74nhCJrvQHqLAtE8nT6uwJ4LYBymSTHKxUM4BG00D7VRA8SR8atrt95csnO8UWhHdchdxamrxodyY51mBzZ5feX3rAmNX1PdHNMpZU3UfIfD6PVGCVnoWtttCLH0Ilni4N6NphYVGQIBECGj0xsT8YqHYM1DJYPikTWamGdu25NN1RJo4aEcwEL1trUWlnV3tugcyF61cJ9VOmt8GoeF2aGzZXdH7Pz68RIVbMGq7LdJYGUwgBCCZQjN5GKZzV21iP5rzczmvBwinp0z3TEfeDn5YRyL3iqApcUIbVBxTlCUCBqhVAOAltNdIvTdzwHRcFkDM8aXRKoq4MxbTR2fMcgCm8X78Q8b708blMSFCvYRVEpwzZWBOtvUciSow519giKVqp6M4kpDWMS2CZMfSUFJdRotgwsofYh0ifumfVuItOcpmOjqSekYMZjiizgDNwG3uDkPENk95tBFXVi6xUABxxb5bTh9e6bf2ilzhy8bPTunrGw"
    send_response = request_send_standup(token, channel_id, message)
    
    assert send_response.status_code == InputError.code

# No standup active
def test_standup_send_no_active(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    request_start_standup(token, channel_id, 1)
    time.sleep(2)

    send_response = request_send_standup(token, channel_id, "Hi")

    assert send_response.status_code == InputError.code


# Not a member of the channel
def test_standup_send_not_member(clear_data):
    user1 = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token1 = user1["token"]

    user2 = request_register("chopin@gmail.com", "password1", "frederic", "chopin").json()
    token2 = user2["token"]

    channel = request_channels_create(token1, "Channel1", True).json()
    channel_id = channel["channel_id"]

    send_response = request_send_standup(token2, channel_id, "Hi")

    assert send_response.status_code == AccessError.code
    
# Returns empty dict
def test_standup_send_return_type(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    request_start_standup(token, channel_id, 1)

    send_response = request_send_standup(token, channel_id, "Cya").json()

    assert send_response == {}

    time.sleep(2)


# Basic case of testing whether message was sent correctly                       
def test_standup_send_basic_message(clear_data):
    user = request_register("liszt@gmail.com", "password1", "franz", "liszt").json()
    token = user["token"]

    channel = request_channels_create(token, "Channel1", True).json()
    channel_id = channel["channel_id"]

    request_start_standup(token, channel_id, 2)

    request_send_standup(token, channel_id, "Is")
    request_send_standup(token, channel_id, "this")
    request_send_standup(token, channel_id, "working?")
    
    time.sleep(2.5)

    messages = get_channel_messages(token, channel_id, 0).json()

    assert messages['messages'][0]['message'] == \
    '''franzliszt: Is
franzliszt: this
franzliszt: working?
'''
