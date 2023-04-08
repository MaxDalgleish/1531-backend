import pytest
import requests
from src import config
from src.error import AccessError, InputError
import tests.test_helpers as th

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")


# Test if sharing message with invalid token raises an AccessError
def test_message_share_invalid_token(clear_data):

    # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 send a dm
    send_response = th.message_senddm(token2, dm_id, "I thought you wanted to dance")
    send_response = send_response.json()
    
    # Share the dm message given an invalid token
    share_response = th.message_share(th.invalid_token1(), send_response['message_id'], "", -1, dm_id)

    assert share_response.status_code == AccessError.code
    
# Test if sharing message with invalid channel id raises an InputError
def test_message_share_channel_id_invalid(clear_data):

     # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a channel and save response
    channel_response = th.channels_create(token1, "Valorant", True)
    channel_response = channel_response.json()

    channel_id = channel_response['channel_id']
    
    # User2 joins channel
    th.channel_join(token2, channel_id)

    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 sends a dm
    send_response = th.message_senddm(token2, dm_id, "Fish Icecream")
    send_response = send_response.json()
    
    # User2 shares the dm message to channel given invalid channel id
    share_response = th.message_share(token2, send_response['message_id'], "", (channel_id + 1), -1)

    assert share_response.status_code == InputError.code

# Test if sharing message with invalid dm id raises an InputError
def test_message_share_dm_id_invalid(clear_data):

     # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a channel and save response
    channel_response = th.channels_create(token1, "Valorant", True)
    channel_response = channel_response.json()

    channel_id = channel_response['channel_id']
    
    # User2 joins channel
    th.channel_join(token2, channel_id)
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 sends a dm
    send_response = th.message_senddm(token2, dm_id, "Fish Icecream")
    send_response = send_response.json()
    
    # User2 shares the dm message to channel given invalid channel id
    share_response = th.message_share(token2, send_response['message_id'], "", -1, dm_id + 1)

    assert share_response.status_code == InputError.code
    
# Test whether InputError is raised given invalid channel and dm id
def test_message_share_channel_and_dm_id_invalid(clear_data):
    
    # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a channel and save response
    channel_response = th.channels_create(token1, "Kitty", True)
    channel_response = channel_response.json()

    channel_id = channel_response['channel_id']
    
    # User 2 joins channel
    th.channel_join(token2, channel_id)
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 sends a dm message
    send_response = th.message_senddm(token2, dm_id, "Summertime in Paris")
    send_response = send_response.json()
    
    # User2 shares the dm message given invalid channel and dm id
    share_response = th.message_share(token2, send_response['message_id'], "", channel_id + 1, dm_id + 1)

    assert share_response.status_code == InputError.code
    
# Test whether InputError is raised when channel and dm id are both valid
def test_message_share_neither_channel_or_dm_id_minus_one(clear_data):

    # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a channel and save response
    channel_response = th.channels_create(token1, "Justin", True)
    channel_response = channel_response.json()

    channel_id = channel_response['channel_id']
    
    # User 2 joins channel
    th.channel_join(token2, channel_id)
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 sends a dm message
    send_response = th.message_senddm(token2, dm_id, "Fish Icecream")
    send_response = send_response.json()
    
    # User2 shares the dm message given both channel and dm id
    share_response = th.message_share(token2, send_response['message_id'], "", channel_id, dm_id)

    assert share_response.status_code == InputError.code

# Test whether InputError raised if the og message id is invalid
def test_message_share_og_message_id_invalid(clear_data):
    
    # Register user 1
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user 2
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a channel and save response
    channel_response = th.channels_create(token1, 'Valorant', True)
    channel_response = channel_response.json()

    channel_id = channel_response['channel_id']
    
    # User2 joins channel
    th.channel_join(token2, channel_id)
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']
    
    # User2 sends a dm
    send_response = th.message_senddm(token2, dm_id, "Fish Icecream")
    send_response = send_response.json()
    
    # User2 shares the dm message to channel given invalid og message id
    share_response = th.message_share(token2, send_response['message_id'] + 1, "", channel_id, -1)

    assert share_response.status_code == InputError.code

# Test if inputerror is raised when message with length over 1000 is shared
def test_message_share_len_over_1000(clear_data):
    
    # Register user1 and save response
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()

    dm_id = dm_create_response['dm_id']

    # User2 sends a dm message with length 996
    send_response = th.message_senddm(token2, dm_id, "2gXbqVdmsomGlCxhwYSWOxWJ6gOgW5Lrjlvt44SoQOeSCY4yozzZNfkD9w0VJ9iTrwbDaSX3zkGpDS6HWyXqFwa5jMtPY49wiJ2uabTGEEGPBEbtAnVlpgS0maFGFEDUwd70P7f5aolhPiatLRmuCT50Z0hd72DHhKnR38zmgmsOERfbVNw49TtKqFe1Kk9xD8KRqt2LmDoo04q9OTSH4rQe0CYw3gTAu27FBczjGr5h56QSYWqpVbBGZ8QrFF49BLHczv7DWQJm0ZQ9bOMarITFWDI4NvaTBSKq5H9ql65iuWraeviNMPAk8YSx9oXuYVw14XXL4fd8A9GkwopyrQE83eb7G3dnTyclzMxNhBejtNGxGJyu8WgR0hitVnmbHZY3N6v3xODCxGc70xYEhMhAd4ahw9VYZRw739BAZSoYagRAsuQ0TrYeMXffyNRbTDIIRo4rGaD4zOgnFEcLzg6d3V1SVrb6IgP0JFGJJI3j0QbdTRPh5JaLU4wx4ViKZkfmKT4wC4C0JlEzUTAwPR38nXFskWlfrugUcEuzkANJueSWzMWrSlza2WWlLTidm41latBvBS5iuje7lrPNOaNSnYiCZaXrkoyKdC3YwQafDR31dnZG1vxOz9TEfQkYamdG6KtDfrOcyUJxmIGlDplrmPWEeTRrIWxFtAVYEyE9LpbTHjx84urhPXHPBIKmSNJqGUCfXugCijW5kgovzCtm0vh9udS3f3RJkPlZNG0Buoh2ZEpPxufqJXYKgBCFnirdE49GFYw5HvJ7gtHlVA5KGMS0Cb5krLznBDU7NuTXUgljpQEzoTMRKP46StpcMvuYaJ0nlZ5tJooOcB3hRagG8iAQk8uxsFdNxhMgQzp1hkIn1duiBVtyt5jURLhwmAXuGfe888mgMT3Sev6w7H1QLTkkgZ1Aqlu3qMVjl0jF1tbQiGJiiBO8dEn8xJrFuBwCe9SlyaFyzXxLKhhSNIMSYnEdHgmkPHoJ")
    send_response = send_response.json()
    
    # User2 shares the dm message given message length over 1000
    share_response = th.message_share(token2, send_response['message_id'], "2gXbqVdmsomGlCxhionqiwdoqiwdioqwndoiqnwodwYSWOxWJ6gOgW5Lrjlvt44SoQOeSCY4yozzZNfkD9w0VJ9iTrwbDaSX3zkGpDS6HWyXqFwa5jMtPY49wiJ2uabTGEEGPBEbtAnVlpgS0maFGFEDUwd70P7f5aolhPiatLRmuCT50Z0hd72DHhKnR38zmgmsOERfbVNw49TtKqFe1Kk9xD8KRqt2LmDoo04q9OTSH4rQe0CYw3gTAu27FBczjGr5h56QSYWqpVbBGZ8QrFF49BLHczv7DWQJm0ZQ9bOMarITFWDI4NvaTBSKq5H9ql65iuWraeviNMPAk8YSx9oXuYVw14XXL4fd8A9GkwopyrQE83eb7G3dnTyclzMxNhBejtNGxGJyu8WgR0hitVnmbHZY3N6v3xODCxGc70xYEhMhAd4ahw9VYZRw739BAZSoYagRAsuQ0TrYeMXffyNRbTDIIRo4rGaD4zOgnFEcLzg6d3V1SVrb6IgP0JFGJJI3j0QbdTRPh5JaLU4wx4ViKZkfmKT4wC4C0JlEzUTAwPR38nXFskWlfrugUcEuzkANJueSWzMWrSlza2WWlLTidm41latBvBS5iuje7lrPNOaNSnYiCZaXrkoyKdC3YwQafDR31dnZG1vxOz9TEfQkYamdG6KtDfrOcyUJxmIGlDplrmPWEeTRrIWxFtAVYEyE9LpbTHjx84urhPXHPBIKmSNJqGUCfXugCijW5kgovzCtm0vh9udS3f3RJkPlZNG0Buoh2ZEpPxufqJXYKgBCFnirdE49GFYw5HvJ7gtHlVA5KGMS0Cb5krLznBDU7NuTXUgljpQEzoTMRKP46StpcMvuYaJ0nlZ5tJooOcB3hRagG8iAQk8uxsFdNxhMgQzp1hkIn1duiBVtyt5jURLhwmAXuGfe888mgMT3Sev6w7H1QLTkkgZ1Aqlu3qMVjl0jF1tbQiGJiiBO8dEn8xJrFuBwCe9SlyaFyzXxLKhhSNIMSYnEdHgmkPHoJ", -1, dm_id)
    
    assert share_response.status_code == InputError.code

# Test if accesserror is raised when user who hasnt joined any dm or channel 
# tries to share a message
def test_message_share_not_a_member(clear_data):
    
    # Register user1 and save response
    register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
    token1 = register_response1['token']
    
    # Register user2 and save response
    register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
    token2 = register_response2['token']
    auth_user_id2 = register_response2['auth_user_id']
    
    # Register user3 and save response
    register_response3 = th.auth_register("Derrick@gmail.com", 'password000', 'Derrick', 'Doan').json()
    token3 = register_response3['token']
    
    # User1 creates a channel
    channel_create_response = th.channels_create(token1, 'Detroit', True)
    channel_create_response_data = channel_create_response.json()

    channel_id = channel_create_response_data['channel_id']
    
    # User2 joins channel
    th.channel_join(token2, channel_id)
    
    # User2 send a message in the channel
    send_channel_response = th.message_send(token2, channel_id, "Dunked")
    send_channel_response = send_channel_response.json()
    
    # User1 creates a dm with user2
    dm_create_response = th.dm_create(token1, [auth_user_id2])
    dm_create_response = dm_create_response.json()
    dm_id = dm_create_response['dm_id']

    # User2 sends a dm message
    send_dm_response = th.message_senddm(token2, dm_create_response['dm_id'], "Icey")
    send_dm_response = send_dm_response.json()
    
    # User3 attempts to share the channel message to dm
    share_response1 = th.message_share(token3, send_channel_response['message_id'], "", -1, dm_id)
    
    # User3 attempts to share the dm message to channel
    share_response2 = th.message_share(token3, send_dm_response['message_id'], "", channel_id, -1)
    
    assert share_response1.status_code == AccessError.code
    assert share_response2.status_code == AccessError.code

def test_user_is_not_member_of_og_channel_or_dm(clear_data):
      # Register user1 and save response
      register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
      token1 = register_response1['token']
    
      # Register user2 and save response
      register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
      token2 = register_response2['token']

    
      # Register user3 and save response
      register_response3 = th.auth_register("Derrick@gmail.com", 'password000', 'Derrick', 'Doan').json()
    
      # User1 creates a channel
      channel_create_response = th.channels_create(token1, 'Detroit', True)
      channel_create_response_data = channel_create_response.json()
      channel_id = channel_create_response_data['channel_id']
    
      # User2 creates a dm
      dm_create_response = th.dm_create(token2, [register_response3['auth_user_id']])
      dm_create_response = dm_create_response.json()

      # User2 creates a channel
      channel_create_response2 = th.channels_create(token2, 'Texas', True)
      channel_create_response2 = channel_create_response2.json()
      channel_id2 = channel_create_response2['channel_id']

      # User2 sends a message in the dm
      dm_message_send = th.message_senddm(token2, dm_create_response['dm_id'], 'Testing.')
      dm_message_send = dm_message_send.json()

      # User 2 sends a message in the channel
      channel_send_response = th.message_send(token2, channel_id2, "Dunked")
      channel_send_response = channel_send_response.json()

      # User 1 attempts to send a message to the channel
      share_response1 = th.message_share(token1, dm_message_send['message_id'], '', channel_id, -1)

      # User 1 attempts to send a message to the channel
      share_response2 = th.message_share(token1, channel_send_response['message_id'], '', channel_id, -1)

      assert share_response1.status_code == InputError.code
      assert share_response2.status_code == InputError.code

# Test for checking if the message is too long and test for if functions works properly    
def test_message_length_too_long_and_success(clear_data):
      # Register user1 and save response
      register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
      token1 = register_response1['token']
    
      # User1 creates a channel
      channel_create_response = th.channels_create(token1, 'Detroit', True)
      channel_create_response_data = channel_create_response.json()
      channel_id = channel_create_response_data['channel_id']

      # User1 creates a channel
      channel_create_response2 = th.channels_create(token1, 'Texas', True)
      channel_create_response2 = channel_create_response2.json()
      channel_id2 = channel_create_response2['channel_id']

      # User 1 sends a message in the channel
      channel_send_response = th.message_send(token1, channel_id2, "Dunked")
      channel_send_response = channel_send_response.json()

      # User 1 attempts to send a message to the channel with a message length of >1000
      share_response = th.message_share(token1, channel_send_response['message_id'], 'gXbnasidnqiwndiqnwdiqnwidnqwidnqiwdnqiwndiqwndiqndiqwqVdmsomGlCxhwYSWOxWJ6gOgW5Lrjlvt44SoQOeSCY4yozzZNfkD9w0VJ9iTrwbDaSX3zkGpDS6HWyXqFwa5jMtPY49wiJ2uabTGEEGPBEbtAnVlpgS0maFGFEDUwd70P7f5aolhPiatLRmuCT50Z0hd72DHhKnR38zmgmsOERfbVNw49TtKqFe1Kk9xD8KRqt2LmDoo04q9OTSH4rQe0CYw3gTAu27FBczjGr5h56QSYWqpVbBGZ8QrFF49BLHczv7DWQJm0ZQ9bOMarITFWDI4NvaTBSKq5H9ql65iuWraeviNMPAk8YSx9oXuYVw14XXL4fd8A9GkwopyrQE83eb7G3dnTyclzMxNhBejtNGxGJyu8WgR0hitVnmbHZY3N6v3xODCxGc70xYEhMhAd4ahw9VYZRw739BAZSoYagRAsuQ0TrYeMXffyNRbTDIIRo4rGaD4zOgnFEcLzg6d3V1SVrb6IgP0JFGJJI3j0QbdTRPh5JaLU4wx4ViKZkfmKT4wC4C0JlEzUTAwPR38nXFskWlfrugUcEuzkANJueSWzMWrSlza2WWlLTidm41latBvBS5iuje7lrPNOaNSnYiCZaXrkoyKdC3YwQafDR31dnZG1vxOz9TEfQkYamdG6KtDfrOcyUJxmIGlDplrmPWEeTRrIWxFtAVYEyE9LpbTHjx84urhPXHPBIKmSNJqGUCfXugCijW5kgovzCtm0vh9udS3f3RJkPlZNG0Buoh2ZEpPxufqJXYKgBCFnirdE49GFYw5HvJ7gtHlVA5KGMS0Cb5krLznBDU7NuTXUgljpQEzoTMRKP46StpcMvuYaJ0nlZ5tJooOcB3hRagG8iAQk8uxsFdNxhMgQzp1hkIn1duiBVtyt5jURLhwmAXuGfe888mgMT3Sev6w7H1QLTkkgZ1Aqlu3qMVjl0jF1tbQiGJiiBO8dEn8xJrFuBwCe9SlyaFyzXxLKhhSNIMSYnEdHgmkPHoJ', channel_id, -1)

      assert share_response.status_code == InputError.code

      # User 1 attempts to send a message to the channel
      share_response = th.message_share(token1, channel_send_response['message_id'], 'Hello', channel_id, -1)
      share_response = share_response.json()

      assert share_response['shared_message_id'] == 2

# Test for checking if a given message doesn't exist and if the user isn't a member of the channel where it came from
def test_message_doesnt_exist_and_not_og_channel_member(clear_data):

      # Register user1 and save response
      register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
      token1 = register_response1['token']
    
      # Register user2 and save response
      register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
      token2 = register_response2['token']

    
      # Register user3 and save response
      register_response3 = th.auth_register("Derrick@gmail.com", 'password000', 'Derrick', 'Doan').json()


      # Creating a dm with user2 and user3
      dm_create_response = th.dm_create(token2, [register_response3['auth_user_id']])
      dm_create_response = dm_create_response.json()
      dm_id = dm_create_response['dm_id']

      # User1 creates a channel
      channel_create_response = th.channels_create(token1, 'Detroit', True)
      channel_create_response_data = channel_create_response.json()
      channel_id = channel_create_response_data['channel_id']

      # User 1 sends a message in the channel
      channel_send_response = th.message_send(token1, channel_id, 'Dunked')
      channel_send_response = channel_send_response.json()

      # Attempt for user2 to share the message in the channel to the dm with a invalid message_id
      share_response = th.message_share(token2, channel_send_response['message_id'] + 1, '', -1, dm_id)

      assert share_response.status_code == InputError.code

      # Attempt for user2 to share the message in the channel to the dm but the user isn't a member
      # of the channel with the original message
      share_response = th.message_share(token2, channel_send_response['message_id'], '', -1, dm_id)

      assert share_response.status_code == InputError.code

      # User2 joins a channel
      th.channel_join(token2, channel_id)

      # Attempt for user2 to share the message in the channel to the dm but the message is greater than 1000 characters
      # And an input error is raised
      share_response = th.message_share(token2, channel_send_response['message_id'], '2gXbnasidnqiwndiioiqnwoidnqowindqoiwndoqiwndoqiwndoqiwndoqiwqnwdiqnwidnqwidnqiwdnqiwndiqwndiqndiqwqVdmsomGlCxhwYSWOxWJ6gOgW5Lrjlvt44SoQOeSCY4yozzZNfkD9w0VJ9iTrwbDaSX3zkGpDS6HWyXqFwa5jMtPY49wiJ2uabTGEEGPBEbtAnVlpgS0maFGFEDUwd70P7f5aolhPiatLRmuCT50Z0hd72DHhKnR38zmgmsOERfbVNw49TtKqFe1Kk9xD8KRqt2LmDoo04q9OTSH4rQe0CYw3gTAu27FBczjGr5h56QSYWqpVbBGZ8QrFF49BLHczv7DWQJm0ZQ9bOMarITFWDI4NvaTBSKq5H9ql65iuWraeviNMPAk8YSx9oXuYVw14XXL4fd8A9GkwopyrQE83eb7G3dnTyclzMxNhBejtNGxGJyu8WgR0hitVnmbHZY3N6v3xODCxGc70xYEhMhAd4ahw9VYZRw739BAZSoYagRAsuQ0TrYeMXffyNRbTDIIRo4rGaD4zOgnFEcLzg6d3V1SVrb6IgP0JFGJJI3j0QbdTRPh5JaLU4wx4ViKZkfmKT4wC4C0JlEzUTAwPR38nXFskWlfrugUcEuzkANJueSWzMWrSlza2WWlLTidm41latBvBS5iuje7lrPNOaNSnYiCZaXrkoyKdC3YwQafDR31dnZG1vxOz9TEfQkYamdG6KtDfrOcyUJxmIGlDplrmPWEeTRrIWxFtAVYEyE9LpbTHjx84urhPXHPBIKmSNJqGUCfXugCijW5kgovzCtm0vh9udS3f3RJkPlZNG0Buoh2ZEpPxufqJXYKgBCFnirdE49GFYw5HvJ7gtHlVA5KGMS0Cb5krLznBDU7NuTXUgljpQEzoTMRKP46StpcMvuYaJ0nlZ5tJooOcB3hRagG8iAQk8uxsFdNxhMgQzp1hkIn1duiBVtyt5jURLhwmAXuGfe888mgMT3Sev6w7H1QLTkkgZ1Aqlu3qMVjl0jF1tbQiGJiiBO8dEn8xJrFuBwCe9SlyaFyzXxLKhhSNIMSYnEdHgmkPHoJ', -1, dm_id)

      assert share_response.status_code == InputError.code

# User isn't a member of the dm that the message comes from but then joins the dm
def test_not_dm_member(clear_data):
      # Register user1 and save response
      register_response1 = th.auth_register("justin@gmail.com", 'password123', 'Justin', 'Son').json()
      token1 = register_response1['token']
    
      # Register user2 and save response
      register_response2 = th.auth_register("cynthia@gmail.com", "password123456", 'Cynthia', "Li").json()
      token2 = register_response2['token']
    
      # Register user3 and save response
      register_response3 = th.auth_register("Derrick@gmail.com", 'password000', 'Derrick', 'Doan').json()
      token3 = register_response3['token']

      # Creating a dm with user1 and user2
      dm_create_response1 = th.dm_create(token1, [register_response2['auth_user_id']])
      dm_create_response1 = dm_create_response1.json()
      dm_id1 = dm_create_response1['dm_id']

      # Creating a dm wth user2 and user 3
      dm_create_response2 = th.dm_create(token2, [register_response3['auth_user_id']])
      dm_create_response2 = dm_create_response2.json()
      dm_id2 = dm_create_response2['dm_id']

      # User1 sends a message in a dm
      send_response1 = th.message_senddm(token1, dm_id1, 'I thought you wanted to dance')
      send_response1 = send_response1.json()

      # Attempt for user3 to share the message in the the second dm
      share_response1 = th.message_share(token3, send_response1['message_id'], '', -1, dm_id2)

      assert share_response1.status_code == InputError.code

      # Attempt for user2 to share the message in the second dm
      share_response2 = th.message_share(token2, send_response1['message_id'], '', -1, dm_id2)
      share_response2 = share_response2.json()

      assert share_response2['shared_message_id'] == 2
