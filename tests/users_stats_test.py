import pytest
import requests
from src import config
from src.error import AccessError
from datetime import datetime, timedelta
import time
import datetime


from .test_helpers import request_message_sendlater, \
                          request_send_standup, \
                          request_user_stats, \
                          request_register, \
                          request_channels_create, \
                          request_dm_create, \
                          request_message_senddm, \
                          request_message_send, \
                          request_channel_invite, \
                          request_message_remove, \
                          invalid_token1, \
                          request_users_stats, \
                          request_dm_remove, \
                          request_channel_join, \
                          request_remove_user, \
                          request_start_standup

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test AccessError is raised if token is invalid
def test_users_stats_invalid_token(clear_data):

    stats_response = request_user_stats(invalid_token1())
    
    assert stats_response.status_code == AccessError.code

# Test that all metrics are 0 when first user registers
def test_users_stats_starting_metrics(clear_data):
    
    user1 = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user1 = user1.json()

    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    assert users_stats['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

    assert users_stats['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

    assert users_stats['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert users_stats['workspace_stats']['messages_exist'][0]['time_stamp'] - curr_time < 2

    assert users_stats['workspace_stats']['utilization_rate'] == 0

# Test channels_exist is correct and time is correct
def test_users_stats_channels_exist(clear_data):

    # Register 2 users
    user1 = request_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = request_register("bbb@gmail.com", "12345678", "Allan", "Z")
    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 3 channels
    channel1 = request_channels_create(user1['token'], "Totoro", True)
    channel1 = channel1.json()
    request_channels_create(user1['token'], "CaramelPopcorn", False)
    request_channels_create(user1['token'], "Pizza", True)

    # User1 sends a message in channel1
    request_message_send(user1['token'], channel1['channel_id'], "blahblahblah")

    # User1 creates a dm
    request_dm_create(user2['token'], [])

    # User2 creates 2 channels
    request_channels_create(user2['token'], "BojackHorseman", True)
    request_channels_create(user2['token'], "SquidGame", False)

    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()
    
    # Get users stats
    users_stats2 = request_users_stats(user2['token'])
    users_stats2 = users_stats2.json()
    
    # Get current time_stamp
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that details are correct
    assert users_stats['workspace_stats']['channels_exist'][5]['num_channels_exist'] == 5
    assert users_stats['workspace_stats']['dms_exist'][1]['num_dms_exist'] == 1
    assert users_stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1
    
    # Check the time_stamp is within a second of the time of the request
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

# Test dms_exist is correct
def test_users_stats_dms_exist(clear_data):

    # Register 2 users
    user1 = request_register("abcd@gmail.com", "password", "Stan", "Lee")
    user2 = request_register("efgh@gmail.com", "12345678", "Captain", "America")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 4 dms with themself
    dm1 = request_dm_create(user1['token'], [])
    dm1 = dm1.json()
    request_dm_create(user1['token'], [])
    request_dm_create(user1['token'], [])
    request_dm_create(user1['token'], [])

    # User2 creates 3 dms with user1
    request_dm_create(user2['token'], [user1['auth_user_id']])
    request_dm_create(user2['token'], [user1['auth_user_id']])
    request_dm_create(user2['token'], [user1['auth_user_id']])

    # User1 creates a channel
    channel1 = request_channels_create(user1['token'], "SquidGame", False)
    channel1 = channel1.json()

    # User1 sends a message in dm1 and channel1
    request_message_senddm(user1['token'], dm1['dm_id'], "Player 067 eliminated")
    request_message_send(user1['token'], channel1['channel_id'], "hellohellohello")

    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()

    # Get current time_stamp
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that details are correct
    assert users_stats['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1
    assert users_stats['workspace_stats']['dms_exist'][7]['num_dms_exist'] == 7
    assert users_stats['workspace_stats']['messages_exist'][2]['num_messages_exist'] == 2
    
    # Check that dms_exist is correct and time_stamp is within a second of the 
    # request being sent
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

# Test if dms_exist decreases if a dm is removed
def test_users_stats_dms_decrease(clear_data):

    # Create 2 users
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user2 = request_register("world@gmail.com", "12345678", "Hermione", "Granger")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 3 dms
    dm1 = request_dm_create(user1['token'], [])
    dm2 = request_dm_create(user1['token'], [])
    dm3 = request_dm_create(user1['token'], [])

    dm1 = dm1.json()
    dm2 = dm2.json()
    dm3 = dm3.json()

    # User2 creates 2 more dms
    request_dm_create(user2['token'], [])
    request_dm_create(user2['token'], [])

    # Get users stats
    users_stats1 = request_users_stats(user1['token'])
    users_stats1 = users_stats1.json()

    # Check that num_dms_exist is correct
    assert users_stats1['workspace_stats']['dms_exist'][5]['num_dms_exist'] == 5

    # User1 removes the first 3 dms
    request_dm_remove(user1['token'], dm1['dm_id'])
    request_dm_remove(user1['token'], dm2['dm_id'])
    request_dm_remove(user1['token'], dm3['dm_id'])

    # Check that num_dms_exist decreases by 3
    users_stats2 = request_users_stats(user1['token'])
    users_stats2 = users_stats2.json()
    
    assert users_stats2['workspace_stats']['dms_exist'][8]['num_dms_exist'] == 2

    # User1 creates 2 more dms
    request_dm_create(user1['token'], [])
    request_dm_create(user1['token'], [])

    # Get users_stats
    users_stats3 = request_users_stats(user2['token'])
    users_stats3 = users_stats3.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that dms_exist is correct and that time_stamp is within a second of
    # the request being sent
    assert users_stats3['workspace_stats']['dms_exist'][10]['num_dms_exist'] == 4
    assert users_stats3['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

# Test if messages_exist is correct
def test_users_stats_messages_exist(clear_data):

    # Register 3 users
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user2 = request_register("world@gmail.com", "12345678", "Hermione", "Granger")
    user3 = request_register("hufflepuff@gmail.com", "0000000", "Ron", "Weasely")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and invites user2 and user3
    channel1 = request_channels_create(user1['token'], "Arietty", True)
    channel1 = channel1.json()
    request_channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    request_channel_invite(user1['token'], channel1['channel_id'], user3['auth_user_id'])

    # User2 creates a channel and invites user1 and user3
    channel2 = request_channels_create(user2['token'], "BinChicken", True)
    channel2 = channel2.json()
    request_channel_invite(user2['token'], channel2['channel_id'], user1['auth_user_id'])
    request_channel_invite(user2['token'], channel2['channel_id'], user3['auth_user_id'])

    # User3 creates 2 dms with themself
    dm1 = request_dm_create(user3['token'], [])
    dm2 = request_dm_create(user3['token'], [])

    dm1 = dm1.json()
    dm2 = dm2.json()

    # User3 sends 3 messages in channel2
    request_message_send(user3['token'], channel2['channel_id'], "giraffe")
    request_message_send(user3['token'], channel2['channel_id'], "rhino")
    request_message_send(user3['token'], channel2['channel_id'], "octopus")

    # User2 sends a message in channel2
    request_message_send(user2['token'], channel2['channel_id'], "cow")

    # User1 sends 2 messages in channel1
    request_message_send(user1['token'], channel2['channel_id'], "sushi")
    request_message_send(user1['token'], channel2['channel_id'], "spaghetti")

    # User3 sends 2 messages in dm1
    request_message_senddm(user3['token'], dm1['dm_id'], "hello")
    request_message_senddm(user3['token'], dm1['dm_id'], "world")

    # User3 sends 2 messages in dm2
    request_message_senddm(user3['token'], dm2['dm_id'], "hello")
    request_message_senddm(user3['token'], dm2['dm_id'], "world")

    # Get users stats
    users_stats = request_users_stats(user3['token'])
    users_stats = users_stats.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that dms_exist is correct and that time_stamp is within a second of
    # the request being sent
    assert users_stats['workspace_stats']['messages_exist'][10]['num_messages_exist'] == 10
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2

# Test if messages_exist decreases when a message is removed
def test_users_stats_messages_decrease(clear_data):

    # Register 2 users
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user2 = request_register("world@gmail.com", "12345678", "Hermione", "Granger")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates a channel
    channel1 = request_channels_create(user1['token'], "Arietty", True)
    channel1 = channel1.json()

    # User2 creates a dm with user1
    dm1 = request_dm_create(user2['token'], [user1['auth_user_id']])
    dm1 = dm1.json()

    # User1 sends 3 messages into channel1
    msg1 = request_message_send(user1['token'], channel1['channel_id'], "giraffe")
    msg2 = request_message_send(user1['token'], channel1['channel_id'], "rhino")
    msg3 = request_message_send(user1['token'], channel1['channel_id'], "octopus")

    msg1 = msg1.json()
    msg2 = msg2.json()
    msg3 = msg3.json()

    # User2 sends 2 messages in dm1
    msg4 = request_message_senddm(user2['token'], dm1['dm_id'], "I'm so bored")
    msg5 = request_message_senddm(user2['token'], dm1['dm_id'], "://////")

    msg4 = msg4.json()
    msg5 = msg5.json()

    # Get users stats
    users_stats1 = request_users_stats(user1['token'])
    users_stats1 = users_stats1.json()

    # Check that num_messages_exist is correct
    assert users_stats1['workspace_stats']['messages_exist'][5]['num_messages_exist'] == 5

    # User1 removes first 3 messages in channel1
    request_message_remove(user1['token'], msg1['message_id'])
    request_message_remove(user1['token'], msg2['message_id'])
    request_message_remove(user1['token'], msg3['message_id'])

    # User2 removes 2 messages in dm1
    request_message_remove(user2['token'], msg4['message_id'])
    request_message_remove(user2['token'], msg5['message_id'])

    # Get users stats
    users_stats2 = request_users_stats(user2['token'])
    users_stats2 = users_stats2.json()

    # Check that num_messages_exist is correct
    assert users_stats2['workspace_stats']['messages_exist'][10]['num_messages_exist'] == 0

    # User1 sends 2 messages into channel1
    request_message_send(user1['token'], channel1['channel_id'], "crab")
    request_message_send(user1['token'], channel1['channel_id'], "snail")

    # Get users stats
    users_stats2 = request_users_stats(user2['token'])
    users_stats2 = users_stats2.json()

    # Get curr time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that num_messages_exist is correct and time_stamp is within a second
    # of the time the request was sent
    assert users_stats2['workspace_stats']['messages_exist'][12]['num_messages_exist'] == 2
    assert users_stats2['workspace_stats']['messages_exist'][0]['time_stamp'] - curr_time < 2

# Test if time_stamps are correctly updated
def test_users_stats_time_stamp(clear_data):

    # Register 2 users
    user1 = request_register("hello@gmail.com", "password", "Pika", "Pika")
    user2 = request_register("world@gmail.com", "12345678", "Ash", "Ketchum")

    user1 = user1.json()
    user2 = user2.json()
    
    # Get users stats
    users_stats1 = request_users_stats(user1['token'])
    users_stats1 = users_stats1.json()

    # Get current time
    curr_time1 = datetime.datetime.now()
    curr_time1 = int(time.mktime(curr_time1.timetuple()))

    # Check that all time_stamps are correct
    assert users_stats1['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time1 < 2
    assert users_stats1['workspace_stats']['dms_exist'][0]['time_stamp'] - curr_time1 < 2
    assert users_stats1['workspace_stats']['messages_exist'][0]['time_stamp'] - curr_time1 < 2

    # Sleep for 3 seconds
    time.sleep(3)

    # Get users stats again
    users_stats2 = request_users_stats(user2['token'])
    users_stats2 = users_stats2.json()

    # Get current time
    curr_time2 = datetime.datetime.now()
    curr_time2 = int(time.mktime(curr_time2.timetuple()))

    # Check that all time_stamps are updated
    assert users_stats2['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time2 < 2
    assert users_stats2['workspace_stats']['dms_exist'][0]['time_stamp'] - curr_time2 < 2
    assert users_stats2['workspace_stats']['messages_exist'][0]['time_stamp'] - curr_time2 < 2

# Test utilisation rate is correct
def tests_users_stats_ulitization_rate(clear_data):

    # Register 5 users
    user1 = request_register("hello@gmail.com", "password", "Pika", "Pika")
    user2 = request_register("world@gmail.com", "12345678", "To", "toro")
    user3 = request_register("batman@gmail.com", "password", "Bat", "Man")
    user4 = request_register("pokemon@gmail.com", "12345678", "Ash", "Ketchum")
    user5 = request_register("familyguy@gmail.com", "password", "Stewie", "Griffin")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()
    user4 = user4.json()
    user5 = user5.json()

    # Get users stats and check utilization rate is 0
    users_stats1 = request_users_stats(user2['token'])
    users_stats1 = users_stats1.json()

    assert users_stats1['workspace_stats']['utilization_rate'] == 0

    # User1 creates a dm with user2 and user3
    request_dm_create(user1['token'], [user2['auth_user_id'], user3['auth_user_id']])

    # User5 creates a channel
    channel1 = request_channels_create(user5['token'], "Club house", True)
    channel1 = channel1.json()

    # Get user stats and check that utilizatio_rate is 4/5
    users_stats2 = request_users_stats(user4['token'])
    users_stats2 = users_stats2.json()

    assert users_stats2['workspace_stats']['utilization_rate'] == 4 / 5

    # Register 2 more users
    request_register("name@gmail.com", "password", "Taylor", "Swift")
    request_register("object@gmail.com", "12345678", "Timothee", "Chalamet")

    # User 4 joins a channel
    request_channel_join(user4['token'], channel1['channel_id'])

    # Check that utilization_rate is updated
    users_stats3 = request_users_stats(user4['token'])
    users_stats3 = users_stats3.json()

    assert users_stats3['workspace_stats']['utilization_rate'] == 5 / 7

# Test removed users are not being considered in ultilization rate calculation
def test_users_stats_removed_users(clear_data):

    # Create 4 users, user1 is a global owner
    user1 = request_register("hello@gmail.com", "password", "Pika", "Pika")
    user2 = request_register("world@gmail.com", "12345678", "Mike", "Wazowski")
    user3 = request_register("batman@gmail.com", "password", "Bat", "Man")
    user4 = request_register("november@gmail.com", "12345678", "Sponge", "Bob")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()
    user4 = user4.json()

    # User2 creates a dm with user1 and user3
    request_dm_create(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])

    # User1 (a global owner) removes user2
    request_remove_user(user1['token'], user2['auth_user_id'])

    # Get users stats
    users_stats = request_users_stats(user3['token'])
    users_stats = users_stats.json()

    # Check that utilization rate is 2/3
    assert users_stats['workspace_stats']['utilization_rate'] == 2 / 3
    
# Test if stats is correct when register is called after it
def test_users_stats_register_after_stats(clear_data):

    # User1 is a global owner
    user1 = request_register("hello@gmail.com", "password", "Pika", "Pika")
    user1 = user1.json()

    # User1 creates a channel
    channel1 = request_channels_create(user1['token'], "Club house", True)
    channel1 = channel1.json()
    
    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()
    
    assert users_stats['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1
    
    # Register user2
    user2 = request_register("world@gmail.com", "12345678", "Mike", "Wazowski")
    user2 = user2.json()
    
    # User2 creates a channel
    channel2 = request_channels_create(user2['token'], "Pent house", True)
    channel2 = channel2.json()

    # Get users stats
    users_stats2 = request_users_stats(user2['token'])
    users_stats2 = users_stats2.json()

    assert users_stats2['workspace_stats']['channels_exist'][2]['num_channels_exist'] == 2
    
    # Register user3
    user3 = request_register("aquaworld@gmail.com", "123456", "Jordan", "Pippen")
    user3 = user3.json()
    
    # User3 creates a channel
    channel3 = request_channels_create(user3['token'], "Palace house", True)
    channel3 = channel3.json()

    # Get users stats
    users_stats3 = request_users_stats(user3['token'])
    users_stats3 = users_stats3.json()

    assert users_stats3['workspace_stats']['channels_exist'][3]['num_channels_exist'] == 3
    
# Test if stats is correct when sendlater is used
def test_users_stats_sendlater(clear_data):
    
    # Register a user
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user1 = user1.json()

    # User1 creates a channel
    channel = request_channels_create(user1['token'], "Tomb", True)
    channel = channel.json()
    
    # Calculate time in future by 3 seconds
    time_in_future = datetime.datetime.now() + datetime.timedelta(seconds = 3)

    # User1 sends a message into channel using sendlater
    request_message_sendlater(user1['token'], 
                              channel['channel_id'], 
                              "Hello World", 
                              int(time.mktime(time_in_future.timetuple())))
    
    time.sleep(3)

    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that channels_exist is correct and that time_stamp is within a second of
    # the request being sent
    assert users_stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1
    assert users_stats['workspace_stats']['channels_exist'][0]['time_stamp'] - curr_time < 2
    
# Test if stats is correct when standup is used
def test_users_stats_standup(clear_data):
    
    # Register a user
    user1 = request_register("hello@gmail.com", "password", "Harry", "Potter")
    user1 = user1.json()

    # User1 creates a channel
    channel = request_channels_create(user1['token'], "Tomb", True)
    channel = channel.json()
    
    # User1 starts a standup
    request_start_standup(user1['token'], channel['channel_id'], 3)

    # User1 sends a message during the standup
    request_send_standup(user1['token'], channel['channel_id'], "HELLO")
    
    time.sleep(3)

    # Get users stats
    users_stats = request_users_stats(user1['token'])
    users_stats = users_stats.json()

    # Get current time
    curr_time = datetime.datetime.now()
    curr_time = int(time.mktime(curr_time.timetuple()))

    # Check that messages_exist is correct and that time_stamp is within a second of
    # the request being sent
    assert users_stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1
    assert users_stats['workspace_stats']['messages_exist'][1]['time_stamp'] - curr_time < 2