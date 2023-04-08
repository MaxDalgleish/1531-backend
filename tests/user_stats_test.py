import pytest
import requests
from src import config
from src.error import AccessError
import datetime
import time
from .test_helpers import request_channel_join, \
                          request_user_stats, \
                          request_register, \
                          request_channels_create, \
                          request_dm_create, \
                          request_message_senddm, \
                          request_message_send, \
                          request_channel_invite, \
                          request_message_remove, \
                          invalid_token2, \
                          request_channel_leave, \
                          request_dm_leave, \
                          request_dm_remove, \
                          request_start_standup, \
                          request_send_standup

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test that AccessError is raised when invalid token is entered
def test_user_stats_invalid_token(clear_data):

    stats_response = request_user_stats(invalid_token2())
    
    assert stats_response.status_code == AccessError.code
    
def test_user_stats_default_channel_join_then_leave(clear_data):
    
    # Register two users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user1 = user1.json()
    user2 = user2.json()
    
    # User1 creates a channel
    channel1 = request_channels_create(user1['token'], "Totoro", True)
    channel1 = channel1.json()
    
    # User2 joins the created channel
    channel2 = request_channel_join(user2['token'], channel1['channel_id'])
    channel2 = channel2.json()
    
    # User2 then leaves the channel
    request_channel_leave(user2['token'], channel1['channel_id'])

    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()
    
    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    # Check that the number of channels_joined has been updated
    assert user1_stats1['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert user1_stats1['user_stats']['channels_joined'][1]['num_channels_joined'] == 1

    assert user2_stats1['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert user2_stats1['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    assert user2_stats1['user_stats']['channels_joined'][2]['num_channels_joined'] == 0
    
def test_user_stats_default_dm_join_then_leave(clear_data):
    
    # Register two users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user1 = user1.json()
    user2 = user2.json()
    
    # User1 creates a dm with user2
    dm1 = request_dm_create(user1['token'], [user2['auth_user_id']])
    dm1 = dm1.json()
    
    # User2 leaves the created dm
    request_dm_leave(user2['token'], dm1['dm_id'])
    
    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()
    
    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    # Check that the number of dms_joined has been updated
    assert user1_stats1['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert user1_stats1['user_stats']['dms_joined'][1]['num_dms_joined'] == 1
    
    assert user2_stats1['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert user2_stats1['user_stats']['dms_joined'][1]['num_dms_joined'] == 1
    assert user2_stats1['user_stats']['dms_joined'][2]['num_dms_joined'] == 0

def test_user_stats_default_dm_join_then_remove(clear_data):
    
    # Register two users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user1 = user1.json()
    user2 = user2.json()
    
    # User1 creates a dm with user2
    dm1 = request_dm_create(user1['token'], [user2['auth_user_id']])
    dm1 = dm1.json()
    
    # User1 removes the created dm
    request_dm_remove(user1['token'], dm1['dm_id'])

    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()
    
    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    # Check that the number of channels_joined has been updated
    assert user1_stats1['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert user1_stats1['user_stats']['dms_joined'][1]['num_dms_joined'] == 1
    assert user1_stats1['user_stats']['dms_joined'][2]['num_dms_joined'] == 0
    
    assert user2_stats1['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert user2_stats1['user_stats']['dms_joined'][1]['num_dms_joined'] == 1
    assert user2_stats1['user_stats']['dms_joined'][2]['num_dms_joined'] == 0
    
def test_user_stats_default_message_send_then_delete(clear_data):
    
    # Register two users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user1 = user1.json()
    user2 = user2.json()
    
    # User1 creates a channel
    channel = request_channels_create(user1['token'], "TEST", True)
    channel = channel.json()
    
    # User2 joins the created channel
    request_channel_join(user2['token'], channel['channel_id'])
    
    # User2 sends message into the channel
    sent1 = request_message_send(user2['token'], channel['channel_id'], "HELLO")
    sent1 = sent1.json()
    
    # User1 creates a dm with user2
    dm1 = request_dm_create(user1['token'], [user2['auth_user_id']])
    dm1 = dm1.json()
    
    # User2 sends message into the dm
    sent2 = request_message_senddm(user2['token'], dm1['dm_id'], "WORLD")
    sent2 = sent2.json()
    
    # User2 removes both messages from dm and channel
    request_message_remove(user2['token'], sent1['message_id'])
    request_message_remove(user2['token'], sent2['message_id'])
    
    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()
    
    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()
    
    # Check that the number of messages_sent has been updated
    assert user1_stats1['user_stats']['messages_sent'][0]['num_messages_sent'] == 0

    assert user2_stats1['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert user2_stats1['user_stats']['messages_sent'][1]['num_messages_sent'] == 1
    assert user2_stats1['user_stats']['messages_sent'][2]['num_messages_sent'] == 2
    assert user2_stats1['user_stats']['messages_sent'][3]['num_messages_sent'] == 2
    assert user2_stats1['user_stats']['messages_sent'][4]['num_messages_sent'] == 2

# Test that user/stats/v1 returns correctly when involvement is 0 and all
# metrics are 0
def test_user_stats_no_involvement(clear_data):

    # Register user
    user = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user = user.json()
    
    # Call stats
    stats = request_user_stats(user['token'])
    stats = stats.json()

    assert stats['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stats['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stats['user_stats']['involvement_rate'] == 0
    
# Test that time_stamp is within 2 seconds of actual time and is updated 
# each time user/stats/v1 is called
def test_user_stats_timestamp(clear_data):

    user = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user = user.json()
    
    # User creates 2 channels
    channel1 = request_channels_create(user['token'], "CaramelPopcorn", False)
    channel1 = channel1.json()
    request_channels_create(user['token'], "CornIcecream", True)

    # Call user/stats/v1
    stats1 = request_user_stats(user['token'])
    stats1 = stats1.json()

    # Get current timestamp
    curr_time1 = datetime.datetime.now()
    curr_time1 = int(time.mktime(curr_time1.timetuple()))

    # Check that timestamp is within 2 seconds of current time
    assert stats1['user_stats']['channels_joined'][0]['time_stamp'] - curr_time1 < 2

    # User creates 2 dms
    dm1 = request_dm_create(user['token'], [])
    dm1 = dm1.json()
    request_dm_create(user['token'], [])

    time.sleep(2)

    # Call user/stats/v1 again
    stats2 = request_user_stats(user['token'])
    stats2 = stats2.json()

    # Get current timestamp
    curr_time2 = datetime.datetime.now()
    curr_time2 = int(time.mktime(curr_time2.timetuple()))

    # Check that the timestamp for channels_joined is updated and the timestamp
    # for dms_joined is correct
    assert stats2['user_stats']['channels_joined'][0]['time_stamp'] - curr_time2 < 2
    assert stats2['user_stats']['dms_joined'][0]['time_stamp'] - curr_time2 < 2

    # Send a message in the channel and a message in the dm
    request_message_send(user['token'], channel1['channel_id'], "blahblahblah")
    request_message_senddm(user['token'], dm1['dm_id'], "hellohellohello")

    time.sleep(2)

    # Call user/stats/v1 again
    stats3 = request_user_stats(user['token'])
    
    stats3 = stats3.json()

    # Get current timestamp
    curr_time3 = datetime.datetime.now()
    curr_time3 = int(time.mktime(curr_time3.timetuple()))

    # Check that the timestamp for channels_joined and dms_joined is updated and 
    # the timestamp for messages_sent is correct
    assert stats3['user_stats']['channels_joined'][0]['time_stamp'] - curr_time3 < 2
    assert stats3['user_stats']['dms_joined'][0]['time_stamp'] - curr_time3 < 2
    assert stats3['user_stats']['messages_sent'][0]['time_stamp'] - curr_time3 < 2

# Test that channels_joined is correct
def test_user_stats_channels_joined(clear_data):

    # Register two users
    user1 = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = request_register("bbb@gmail.com", "12345678", "Allan", "Z")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 3 channels
    channel1 = request_channels_create(user1['token'], "Totoro", True)
    channel1 = channel1.json()
    request_channels_create(user1['token'], "CaramelPopcorn", False)
    request_channels_create(user1['token'], "Pizza", True)

    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()

    # Check the number of channels joined is correct
    assert user1_stats1['user_stats']['channels_joined'][3]['num_channels_joined'] == 3

    # User2 creates 2 channels
    channel4 = request_channels_create(user2['token'], "CornIcecream", True)
    channel5 = request_channels_create(user2['token'], "ChocolatePopcorn", False)
    channel4 = channel4.json()
    channel5 = channel5.json()

    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    # Check the number of channels joined is correct
    assert user2_stats1['user_stats']['channels_joined'][2]['num_channels_joined'] == 2

    # User1 is invited to user2's channels
    request_channel_invite(user2['token'], 
                           channel4['channel_id'], 
                           user1['auth_user_id'])
    request_channel_invite(user2['token'], 
                           channel5['channel_id'], 
                           user1['auth_user_id'])

    # User1 calls user/stats/v1 again
    user1_stats2 = request_user_stats(user1['token'])
    user1_stats2 = user1_stats2.json()

    # Check that the number of channels_joined has been updated
    assert user1_stats2['user_stats']['channels_joined'][5]['num_channels_joined'] == 5

    # User1 invites user2 to one of its channels
    request_channel_invite(user1['token'], 
                           channel1['channel_id'], 
                           user2['auth_user_id'])

    # User1 calls user/stats/v1 again
    user2_stats2 = request_user_stats(user2['token'])
    user2_stats2 = user2_stats2.json()

    # Check that the number of channels_joined has been updated
    assert user2_stats2['user_stats']['channels_joined'][3]['num_channels_joined'] == 3

# Test that dms_joined is correct
def test_user_stats_dms_joined(clear_data):

    # Register 2 users
    user1 = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = request_register("bbb@gmail.com", "12345678", "Allan", "Z")
    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 3 dms with user2
    request_dm_create(user1['token'], [user2['auth_user_id']])
    request_dm_create(user1['token'], [user2['auth_user_id']])
    request_dm_create(user1['token'], [user2['auth_user_id']])

    # User1 calls user/stats/v1
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()

    # Check the number of dms joined is correct
    assert user1_stats1['user_stats']['dms_joined'][3]['num_dms_joined'] == 3

    # User2 creates 2 dms with just themself
    request_dm_create(user2['token'], [])
    request_dm_create(user2['token'], [])

    # User2 calls user/stats/v1
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    # Check the number of dms joined is correct
    assert user2_stats1['user_stats']['dms_joined'][5]['num_dms_joined'] == 5

# Test that messages_sent is correct
def test_user_stats_msgs_sent(clear_data):

    # Register 3 users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user3 = request_register("ccc@gmail.com", "10000000000", "Max", "D")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and invites user2 and user3
    channel1 = request_channels_create(user1['token'], "Totoro", True)
    channel1 = channel1.json()
    request_channel_invite(user1['token'], 
                           channel1['channel_id'], 
                           user2['auth_user_id'])
    request_channel_invite(user1['token'], 
                           channel1['channel_id'], 
                           user3['auth_user_id'])

    # User2 creates a channel and invites user1 and user3
    channel2 = request_channels_create(user2['token'], "BinChicken", True)
    channel2 = channel2.json()
    request_channel_invite(user2['token'], 
                           channel2['channel_id'], 
                           user1['auth_user_id'])
    request_channel_invite(user2['token'], 
                           channel2['channel_id'], 
                           user3['auth_user_id'])

    # User3 creates a dm with user1 and user2
    dm1 = request_dm_create(user3['token'], 
                            [user1['auth_user_id'], 
                             user2['auth_user_id']])
    dm1 = dm1.json()

    # User1 sends a message in channel1, channel2 and dm1
    request_message_send(user1['token'], 
                         channel1['channel_id'], 
                         "blahblahblah")
    request_message_send(user1['token'],
                         channel2['channel_id'], 
                         "hellohellohello")
    request_message_senddm(user1['token'], 
                           dm1['dm_id'], 
                           "Never gonna give you up")

    # Check the msgs_sent stats for user1 is 3
    user1_stats1 = request_user_stats(user1['token'])
    user1_stats1 = user1_stats1.json()

    assert user1_stats1['user_stats']['messages_sent'][3]['num_messages_sent'] == 3

    # Check the msgs_sent stats for user2 is 0
    user2_stats1 = request_user_stats(user2['token'])
    user2_stats1 = user2_stats1.json()

    assert user2_stats1['user_stats']['messages_sent'][0]['num_messages_sent'] == 0

    # User2 sends 2 messages in the dm
    request_message_senddm(user2['token'], 
                           dm1['dm_id'], 
                           "Never gonna let you down")
    request_message_senddm(user2['token'], 
                           dm1['dm_id'], 
                           "Never gonna run around and desert you")

    # Check the msgs_sent stats for user2 is 2
    user2_stats2 = request_user_stats(user2['token'])
    user2_stats2 = user2_stats2.json()

    assert user2_stats2['user_stats']['messages_sent'][2]['num_messages_sent'] == 2

    # User3 sends a message in channel2
    request_message_send(user3['token'],
                         channel2['channel_id'], 
                         "Fish icecream is gross")

    # Check the msgs_sent stats for user 3
    user3_stats1 = request_user_stats(user3['token'])
    user3_stats1 = user3_stats1.json()

    assert user3_stats1['user_stats']['messages_sent'][1]['num_messages_sent'] == 1

# Test that removing messages does not decrease msgs_sent
def test_user_stats_removed_messages(clear_data):

    # Register User1
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user1 = user1.json()

    # User1 creates a channel
    channel1 = request_channels_create(user1['token'], "Italo", True)
    channel1 = channel1.json()

    # User1 sends 4 messages in the channel
    message1 = request_message_send(user1['token'], channel1['channel_id'], "Never gonna give you up")
    message1 = message1.json()
    request_message_send(user1['token'],
                         channel1['channel_id'], 
                         "Never gonna let you down")
    request_message_send(user1['token'], 
                         channel1['channel_id'],
                         "Never gonna run around and desert you")
    request_message_send(user1['token'], 
                         channel1['channel_id'], 
                         "Never gonna make you cry")

    # Message 1 is removed
    request_message_remove(user1['token'], message1['message_id'])

    # Check that the users' msgs_sent is still 4
    stats1 = request_user_stats(user1['token'])
    stats1 = stats1.json()

    assert stats1['user_stats']['messages_sent'][4]['num_messages_sent'] == 4

    # Send another 2 messages in the channel
    message5 = request_message_send(user1['token'], 
                                    channel1['channel_id'], 
                                    "Never gonna say goodbye")
    message5 = message5.json()
    request_message_send(user1['token'],
                         channel1['channel_id'], 
                         "Never gonna tell a lie and hurt you")

    # Check the users' msgs_sent is 6
    stats2 = request_user_stats(user1['token'])
    stats2 = stats2.json()
    
    assert stats2['user_stats']['messages_sent'][7]['num_messages_sent'] == 6

    # Remove 5th message
    request_message_remove(user1['token'], message5['message_id'])

    # Check the users' msgs_sent is still 6
    stats3 = request_user_stats(user1['token'])
    stats3 = stats3.json()

    assert stats3['user_stats']['messages_sent'][8]['num_messages_sent'] == 6
        
# Test that involvement rate is correct
def test_user_stats_involvement(clear_data):

    # Register 3 users
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user2 = request_register("bbb@gmail.com", "12345678", "Derrick", "D")
    user3 = request_register("ccc@gmail.com", "10000000000", "Max", "D")
    
    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates 5 channels and sends a message in each
    for i in range(0, 5):
        channel = request_channels_create(user1['token'], f"channel{i}", True)
        channel = channel.json()
        request_message_send(user1['token'], channel['channel_id'], str(i))

    # User2 creates 2 dms  and sends a message in each
    dm1 = request_dm_create(user2['token'], [])
    dm2 = request_dm_create(user2['token'], [])

    dm1 = dm1.json()
    dm2 = dm2.json()

    request_message_senddm(user2['token'], dm1['dm_id'], "1")
    request_message_senddm(user2['token'], dm2['dm_id'], "2")

    # Check user1's involvement stats
    user1_stats = request_user_stats(user1['token'])
    user1_stats = user1_stats.json()

    assert user1_stats['user_stats']['involvement_rate'] == \
           (5 + 0 + 5) / (5 + 2 + 7)

    # Check user2's involvemente stats
    user2_stats = request_user_stats(user2['token'])
    user2_stats = user2_stats.json()
    
    assert user2_stats['user_stats']['involvement_rate'] == \
           (0 + 2 + 2) / (5 + 2 + 7)

    # Check that user3's stats is 0
    user3_stats = request_user_stats(user3['token'])
    user3_stats = user3_stats.json()

    assert user3_stats['user_stats']['involvement_rate'] == 0

# Test that involvement rate is capped at 1
def test_user_stats_max_involvement(clear_data):

    # Register a user
    user1 = request_register("aaa@gmail.com", "password", "Allan", "Z")
    user1 = user1.json()

    # Create a channel
    channel1 = request_channels_create(user1['token'], "Tofu", True)
    channel1 = channel1.json()

    # Send 5 messages in the channel and immediately remove them
    for i in range(1, 6):
        request_message_send(user1['token'], channel1['channel_id'], str(i))
        request_message_remove(user1['token'], str(i))
    
    # Send a 6th message
    request_message_send(user1['token'], channel1['channel_id'], "6")

    # Check that involvement rate is capped at 1 even though it would be 6
    stats = request_user_stats(user1['token'])
    stats = stats.json()

    assert stats['user_stats']['involvement_rate'] == 1
    
# Test if stats is correct when standup is used
def test_user_stats_standup(clear_data):
    
    # Register a user
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user1 = user1.json()

    # User1 creates a channel
    channel = request_channels_create(user1['token'], "Tomb", True)
    channel = channel.json()
    
    # User1 starts a standup
    request_start_standup(user1['token'], channel['channel_id'], 3)

    # User1 sends a message during the standup
    request_send_standup(user1['token'], channel['channel_id'], "BYE")
    
    time.sleep(3)

    # Get users stats
    users_stats = request_user_stats(user1['token'])
    users_stats = users_stats.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that messages_sent is correct and that time_stamp is within a second of
    # the request being sent
    assert users_stats['user_stats']['messages_sent'][1]['num_messages_sent'] == 1
    assert users_stats['user_stats']['messages_sent'][1]['time_stamp'] - curr_time < 2
