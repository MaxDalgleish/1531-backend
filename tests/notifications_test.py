import pytest
import requests
from src import config
from src.error import AccessError
import tests.test_helpers as th
from datetime import datetime, timedelta
import time

@pytest.fixture
def clear_data():
    requests.delete(f"{config.url}clear/v1")

# Test that AccessError is raised with invalid token
def test_notifications_invalid_token(clear_data):

    notifications = th.notifications_get(th.invalid_token4())

    assert notifications.status_code == AccessError.code

# Test that tagged notification message works
def test_notifications_tagged(clear_data):

    # Register 3 users
    user1 = th.auth_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = th.auth_register("bbb@gmail.com", "1235678", "Allan", "Z")
    user3 = th.auth_register("aaa@gmail.com", "password", "Max", "D")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # Get their handles
    handle1 = "cynthial"
    handle2 = "allanz"
    handle3 = "maxd"

    # User1 creates a channel and adds user2 and user3
    channel1 = th.channels_create(user1['token'], "CAMELS", True)
    channel1 = channel1.json()
    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    th.channel_invite(user1['token'], channel1['channel_id'], user3['auth_user_id'])

    # User1 and user2 sends messages tagging other users
    th.message_send(user1['token'], channel1['channel_id'], f"@{handle1} @{handle2} @{handle3} are you coming")
    th.message_send(user2['token'], channel1['channel_id'], f"@{handle1} @{handle2} @{handle3} where are you guys")

    # User3 creates 2 dm with user1 and user2
    dm1 = th.dm_create(user3['token'], [user1['auth_user_id'], user2['auth_user_id']])
    dm2 = th.dm_create(user3['token'], [user1['auth_user_id'], user2['auth_user_id']])
    dm1 = dm1.json()
    dm2 = dm2.json()

    dm_name = f"{handle2}, {handle1}, {handle3}"

    # User2 sends messages in both dms and tags other users
    th.message_senddm(user2['token'], dm1['dm_id'], f"Never gonna give you up @{handle1} @{handle3}")
    th.message_senddm(user2['token'], dm2['dm_id'], f"Never gonna @{handle1} give you up @{handle3}")
    th.message_senddm(user2['token'], dm1['dm_id'], f"@{handle1} Never gonna @{handle3} give you up")

    # Get notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check that user1 has correct notifications (should be ordered from most 
    # recent to least recent)

    assert user1_notifications['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: @cynthial Never gonn"   
        },
        {
            'channel_id': -1,
            'dm_id': dm2['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: Never gonna @cynthia"   
        },
        {
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: Never gonna give you"   
        },
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': f"{handle3} added you to {dm_name}"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': f"{handle3} added you to {dm_name}"
        },
        {
            'channel_id': channel1['channel_id'],
            'dm_id': -1,
            'notification_message': f"{handle2} tagged you in CAMELS: @cynthial @allanz @m"
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1,
            'notification_message': f"{handle1} tagged you in CAMELS: @cynthial @allanz @m"
        }
    ]

    assert user2_notifications['notifications'] == [
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': f"{handle3} added you to {dm_name}"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': f"{handle3} added you to {dm_name}"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': f"{handle2} tagged you in CAMELS: @cynthial @allanz @m"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': f"{handle1} tagged you in CAMELS: @cynthial @allanz @m"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': f"{handle1} added you to CAMELS"
        }
    ]

    assert user3_notifications['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: @cynthial Never gonn"   
        },
        {
            'channel_id': -1,
            'dm_id': dm2['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: Never gonna @cynthia"   
        },
        {
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': f"{handle2} tagged you in {dm_name}: Never gonna give you"   
        },
        {
            'channel_id': channel1['channel_id'],
            'dm_id': -1,
            'notification_message': f"{handle2} tagged you in CAMELS: @cynthial @allanz @m"
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1,
            'notification_message': f"{handle1} tagged you in CAMELS: @cynthial @allanz @m"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': f"{handle1} added you to CAMELS"
        }
    ]

# Test that no one is tagged if the handle is invalid
def test_notifications_handle_invalid(clear_data):
    
    # Register 3 users
    user1 = th.auth_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = th.auth_register("bbb@gmail.com", "1235678", "Allan", "Z")
    user3 = th.auth_register("abcd@gmail.com", "password", "Moo", "Cow")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and adds user2
    channel1 = th.channels_create(user1['token'], "CAMELS", True)
    channel1 = channel1.json()
    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])

    # User1 creates a dm with user2
    dm1 = th.dm_create(user1['token'], [user2['auth_user_id']])
    dm1 = dm1.json()

    # User1 and user2 send messages in channel1 and tags non-existent handles
    th.message_send(user1['token'], channel1['channel_id'], f"@jfjd@@!lsjd!! @djhgkjfgndj@ are you coming")
    th.message_send(user2['token'], channel1['channel_id'], f"@nonexistent @@catcatcat@ @ where are you guys@")
    
    # User1 and user2 sends message in channel1 tagging a user that is not a
    # member of the channel
    th.message_send(user1['token'], channel1['channel_id'], f"@moocow @moocow @moocow")
    th.message_send(user2['token'], channel1['channel_id'], f"@moocow @moocow")

    # User1 and user2 sends messages in dm1 and tags non-existent handles
    th.message_senddm(user2['token'], dm1['dm_id'], f"@hello @max @justin")
    th.message_senddm(user1['token'], dm1['dm_id'], f"@goodbye @derrick @justin")

    # User1 and user2 sends messages in dm1 and tags a user who is not a member
    # of the dm
    th.message_senddm(user2['token'], dm1['dm_id'], f"@moocow @moocow")
    th.message_senddm(user1['token'], dm1['dm_id'], f"@moocow")

    # Get users' notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check user3 does not receive any notifications as they were tagged in dms
    # channels they are not in
    assert user3_notifications['notifications'] == []

    # Check that no one receives notifications when non_existent handles are 
    # tagged
    assert user1_notifications['notifications'] == []

    assert user2_notifications['notifications'] == [
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "cynthial added you to allanz, cynthial"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "cynthial added you to CAMELS"
        }
    ]

# Test that reacted notification message works
def test_notifications_react(clear_data):
    
    # Register 2 users
    user1 = th.auth_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = th.auth_register("bbb@gmail.com", "1235678", "Allan", "Z")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates a channel and invites user2
    channel1 = th.channels_create(user1['token'], "CAMELS", True)
    channel1 = channel1.json()
    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])

    # User1 and user2 send messages in channel1
    msg1 = th.message_send(user1['token'], channel1['channel_id'], "hello")
    msg2 = th.message_send(user2['token'], channel1['channel_id'], "goodbye")

    msg1 = msg1.json()
    msg2 = msg2.json()

    # User1 reacts to msg1 and msg2
    th.message_react(user1['token'], msg1['message_id'], 1)
    th.message_react(user1['token'], msg2['message_id'], 1)

    # User2 reacts to msg1 and msg2
    th.message_react(user2['token'], msg1['message_id'], 1)
    th.message_react(user2['token'], msg2['message_id'], 1)

    # User2 creates 2 dms with user1
    dm1 = th.dm_create(user2['token'], [user1['auth_user_id']])
    dm2 = th.dm_create(user2['token'], [user1['auth_user_id']])

    dm1 = dm1.json()
    dm2 = dm2.json()
    
    # User1 and user2 send messages in dms
    msg3 = th.message_senddm(user2['token'], dm1['dm_id'], "I like chocolate")
    msg4 = th.message_senddm(user1['token'], dm2['dm_id'], ":DDDD")

    msg3 = msg3.json()
    msg4 = msg4.json()

    # User1 reacts to user2's dm message
    th.message_react(user1['token'], msg3['message_id'], 1)

    # User2 reacts to user1's dm message
    th.message_react(user2['token'], msg4['message_id'], 1)

    # Get user1 and user2's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()

    # Check that user1's notifications are correct
    assert user1_notifications['notifications'] == [ 
        {   
            'channel_id': -1,
            'dm_id': dm2['dm_id'], 
            'notification_message': 'allanz reacted to your message in allanz, cynthial'
        },
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "allanz added you to allanz, cynthial"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "allanz added you to allanz, cynthial"
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1, 
            'notification_message': 'allanz reacted to your message in CAMELS'
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1, 
            'notification_message': 'cynthial reacted to your message in CAMELS'
        }  
    ]

    assert user2_notifications['notifications'] == [
        {   
            'channel_id': -1,
            'dm_id': dm1['dm_id'], 
            'notification_message': 'cynthial reacted to your message in allanz, cynthial'
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1, 
            'notification_message': 'allanz reacted to your message in CAMELS'
        },
        {   
            'channel_id': channel1['channel_id'],
            'dm_id': -1, 
            'notification_message': 'cynthial reacted to your message in CAMELS'
        },  
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "cynthial added you to CAMELS"
        }
    ]

# Test added to channel/dm notification message works
def test_notifications_added_to_channel_dm(clear_data):
    
    # Register 3 users
    user1 = th.auth_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = th.auth_register("bbb@gmail.com", "1235678", "Allan", "Z")
    user3 = th.auth_register("abcd@gmail.com", "password", "Moo", "Cow")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and adds user2 and user3
    channel1 = th.channels_create(user1['token'], "CAMELS", True)
    channel1 = channel1.json()
    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    th.channel_invite(user1['token'], channel1['channel_id'], user3['auth_user_id'])

    # User2 creates a channel and adds user3
    channel2 = th.channels_create(user2['token'], "GOAT", True)
    channel2 = channel2.json()
    th.channel_invite(user2['token'], channel2['channel_id'], user3['auth_user_id'])

    # User3 creates a dm with user1
    dm1 = th.dm_create(user3['token'], [user1['auth_user_id']])
    dm1 = dm1.json()

    # User2 creates a dm with user1 and user3
    dm2 = th.dm_create(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    dm2 = dm2.json()

    # Get all user1, user2 and user3's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check that user1's notifications are correct
    assert user1_notifications['notifications'] == [
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "allanz added you to allanz, cynthial, moocow"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "moocow added you to cynthial, moocow"
        }
    ]

    assert user2_notifications['notifications'] == [ 
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "cynthial added you to CAMELS"
        }
    ]

    assert user3_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "allanz added you to allanz, cynthial, moocow"
        },
        {
           'channel_id': channel2['channel_id'],
           'dm_id': -1,
           'notification_message': "allanz added you to GOAT"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "cynthial added you to CAMELS"
        }
    ]

# Test 20+ notifications
def test_notifications_over_20_notifications(clear_data):

    # Register 2 users
    user1 = th.auth_register("ccc@gmail.com", "password", "cynthia", "L")
    user2 = th.auth_register("bbb@gmail.com", "1235678", "Allan", "Z")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 6 channels and adds user2 to all of them
    for _ in range (1, 7):
        channel = th.channels_create(user1['token'], "camel", True)
        channel = channel.json()
        th.channel_invite(user1['token'], channel['channel_id'], user2['auth_user_id'])

    # User1 creates 8 dms with user2
    for _ in range(0, 8):
        dm = th.dm_create(user1['token'], [user2['auth_user_id']])
        dm = dm.json()

    # User1 sends 5 messages in channel6 and tags user2 in all of them
    for _ in range(1, 6):
        th.message_send(user1['token'], channel['channel_id'], "hello @allanz")

    # User2 sends 4 messages in dm8
    for _ in range(1, 5):
        th.message_senddm(user2['token'], dm['dm_id'], "I like chocolate")

    # User1 reacts to user2's messages in dm1
    for i in range(6, 10):
        th.message_react(user1['token'], i, 1)

    # Get user2's notifications
    user2_notifications = th.notifications_get(user2['token'])

    user2_notifications = user2_notifications.json()
    user2_notifications = user2_notifications['notifications']

    # Check that only the most recent 20 notifications are returned
    for i in range(0, 4):
        assert user2_notifications[i] == {   
            'channel_id': -1,
            'dm_id': dm['dm_id'], 
            'notification_message': 'cynthial reacted to your message in allanz, cynthial'
        }
    
    for i in range(4, 9):
        assert user2_notifications[i] == {   
            'channel_id': channel['channel_id'],
            'dm_id': -1,
            'notification_message': "cynthial tagged you in camel: hello @allanz"
        }

    counter = 8
    for i in range(9, 17):
        assert user2_notifications[i] == {
            'channel_id': -1,
            'dm_id': counter,
            'notification_message': "cynthial added you to allanz, cynthial"
        }
        counter -= 1

    counter = 6
    for i in range(17, 20):
        assert user2_notifications[i] == {
            'channel_id': counter,
            'dm_id': -1,
            'notification_message': "cynthial added you to camel"
        }
        counter -= 1

# Test tagging edge cases
def test_notifications_tagging_edge_cases(clear_data):
    
    # Register 3 users
    user1 = th.auth_register("pineapple@gmail.com", "password", "spongebob", "squarepants")
    user2 = th.auth_register("rock@gmail.com", "1235678", "PaTrICk", "StaR")
    user3 = th.auth_register("face@gmail.com", "password", "Squid", "Ward")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and user2 and user3 join
    channel = th.channels_create(user1['token'], "neighbours <3333", True)
    channel = channel.json()
    th.channel_join(user2['token'], channel['channel_id'])
    th.channel_join(user3['token'], channel['channel_id'])

    # User2 creates a dm with user1 and user3
    dm = th.dm_create(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    dm = dm.json()

    # User1 sends messages in channel tagging invalid handles (no one should be
    # tagged)
    th.message_send(user1['token'], channel['channel_id'], "@@,dfa@ dkd@j@.d. @hello. @sdjfhldfja@h2@2")
    th.message_send(user1['token'], channel['channel_id'], "he@dfhjak.454857@#$#%$^!@#%$%$@hdfak@48394")
    th.message_send(user1['token'], channel['channel_id'], "#$@ dhfak 3874 @2347#$@$@")

    # User2 sends messages in channel only tagging user1
    th.message_send(user2['token'], channel['channel_id'], "@!#$#$ 3$rt4235@spongebobsquarepants$%#5 @spongebobsquarepants5348")
    th.message_send(user2['token'], channel['channel_id'], "@spongebobsquarepants@##@$ 43$@$@#$ fdfaee")

    # User3 sends messages in the dm tagging invalid handles (no one should be
    # tagged)
    th.message_senddm(user3['token'], dm['dm_id'], "@434342 @ @3 @h @mrkrab #$#@@@@@")
    th.message_senddm(user3['token'], dm['dm_id'], "@mrkrabs#@@@#$4 @53289 @#$%@$% @hdaflfh   ")

    # User1 sends messages in the dm tagging user2 and invalid handles
    th.message_senddm(user1['token'], dm['dm_id'], "@@@patrickstar@@ @h34h2 @##@$@34850 4 847n c479425#$#$%")
    th.message_senddm(user1['token'], dm['dm_id'], "@@354c458#$%$#% #$%@ 3458c duhe@patrickstar@#$%$#")

    # Get each user's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check that notifications are correct
    assert user1_notifications['notifications'] == [ 
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "patrickstar tagged you in neighbours <3333: @spongebobsquarepant"
        },
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "patrickstar tagged you in neighbours <3333: @!#$#$ 3$rt4235@spon"
        },
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "patrickstar added you to patrickstar, spongebobsquarepants, squidward"
        },
    ]

    assert user2_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "spongebobsquarepants tagged you in patrickstar, spongebobsquarepants, squidward: @@354c458#$%$#% #$%@"
        },
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "spongebobsquarepants tagged you in patrickstar, spongebobsquarepants, squidward: @@@patrickstar@@ @h3"
        },
    ]

    assert user3_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "patrickstar added you to patrickstar, spongebobsquarepants, squidward"
        }
    ]

# Test that editing messages to tag users sends the tagged user a notification
def test_notifications_edited_message_tags_users(clear_data):

    # Register 3 users
    user1 = th.auth_register("batman@gmail.com", "password", "bruce", "wayne")
    user2 = th.auth_register("ironman@gmail.com", "1235678", "tony", "stark")
    user3 = th.auth_register("blackwidow@gmail.com", "password", "Natasha", "Romanoff")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates channel1 and invites user2
    channel1 = th.channels_create(user1['token'], "heroes", True)
    channel1 = channel1.json()
    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])

    # User2 creates channel1 and invites user3
    channel2 = th.channels_create(user2['token'], "secret heroes", True)
    channel2 = channel2.json()
    th.channel_invite(user2['token'], channel2['channel_id'], user3['auth_user_id'])

    # User3 creates dm1 with user1 and user3 creates dm2 with user1 and user2
    dm1 = th.dm_create(user3['token'], [user1['auth_user_id']])
    dm2 = th.dm_create(user3['token'], [user1['auth_user_id'], user2['auth_user_id']])
    
    dm1 = dm1.json()
    dm2 = dm2.json()

    # User1 sends a message in channel1 then edits it to tag user2
    msg1 = th.message_send(user1['token'], channel1['channel_id'], "meet me in 10")
    msg1 = msg1.json()
    th.message_edit(user1['token'], msg1['message_id'], "meet me in 10 @tonystark")

    # User2 sends a message in channel1 then edits it to tag user1 and user3 
    # (should only tag user1 as user3 is not a member of the channel)
    msg2 = th.message_send(user2['token'], channel1['channel_id'], "endgame")
    msg2 = msg2.json()
    th.message_edit(user2['token'], msg2['message_id'], "endgame @brucewayne @natasharomanoff")

    # User3 sends a message in channel2 tagging user2 then edits the message 
    # untagging user2(the tagged notification should still show up in user2's 
    # notifications)
    msg3 = th.message_send(user3['token'], channel2['channel_id'], "where you at @tonystark")
    msg3 = msg3.json()
    th.message_edit(user3['token'], msg3['message_id'], "where you at")

    # User3 sends a message in dm1 then edits it to tag user1, user2 and user3 
    # (only user1 and user3 should be tagged as user2 is not a member of the dm)
    msg4 = th.message_senddm(user3['token'], dm1['dm_id'], "hello")
    msg4 = msg4.json()
    th.message_edit(user3['token'], msg4['message_id'], "hello @brucewayne @tonystark @natasharomanoff")

    # User2 sends a message in dm2 tagging user3 then edits it to tag user1
    msg5 = th.message_senddm(user2['token'], dm2['dm_id'], "avengers assemble @natasharomanoff")
    msg5 = msg5.json()
    th.message_edit(user2['token'], msg5['message_id'], "@brucewayne")

    # Get each user's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check that user1's notifications are correct
    assert user1_notifications['notifications'] == [
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, natasharomanoff, tonystark: @brucewayne"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "natasharomanoff tagged you in brucewayne, natasharomanoff: hello @brucewayne @t"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "tonystark tagged you in heroes: endgame @brucewayne "
        },
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "natasharomanoff added you to brucewayne, natasharomanoff, tonystark"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "natasharomanoff added you to brucewayne, natasharomanoff"
        }
    ]

    # Check that user2's notifications are correct
    assert user2_notifications['notifications'] == [
        {   'channel_id': channel2['channel_id'], 
            'dm_id': -1, 
            'notification_message': 'natasharomanoff tagged you in secret heroes: where you at @tonyst'
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne tagged you in heroes: meet me in 10 @tonys"
        },
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "natasharomanoff added you to brucewayne, natasharomanoff, tonystark"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne added you to heroes"
        }
    ]

    # Check that user3's notifications are correct
    assert user3_notifications['notifications'] == [
        {
           'channel_id': -1,
           'dm_id': dm2['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, natasharomanoff, tonystark: avengers assemble @n"
        },
        {
           'channel_id': -1,
           'dm_id': dm1['dm_id'],
           'notification_message': "natasharomanoff tagged you in brucewayne, natasharomanoff: hello @brucewayne @t"
        },
        {
           'channel_id': channel2['channel_id'],
           'dm_id': -1,
           'notification_message': "tonystark added you to secret heroes"
        }
    ]

# Test that users tagged in message/sendlater and message/sendlaterdm recieve
# notifications
def test_notifications_sendlater_tags_users(clear_data):

    # Register 3 users
    user1 = th.auth_register("batman@gmail.com", "password", "bruce", "wayne")
    user2 = th.auth_register("ironman@gmail.com", "1235678", "tony", "stark")
    user3 = th.auth_register("blackwidow@gmail.com", "password", "Natasha", "Romanoff")

    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()

    # User1 creates a channel and user2 and user3 join
    channel = th.channels_create(user1['token'], "Cat lovers", True)
    channel = channel.json()
    th.channel_join(user2['token'], channel['channel_id'])
    th.channel_join(user3['token'], channel['channel_id'])

    # User2 creates a dm with user1 and user3
    dm = th.dm_create(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    dm = dm.json()

    # User3 sends a message with sendlater tagging all users
    later_time = datetime.now() + timedelta(seconds = 1)
    later_time = int(time.mktime(later_time.timetuple()))

    # User3 sends a message with sendlater tagging all users
    th.message_sendlater(user3['token'], channel['channel_id'], 'Hello There @brucewayne, @tonystark, @natasharomanoff', later_time)

    # User2 sends a message with sendlaterdm tagging all users
    th.message_sendlaterdm(user2['token'], dm['dm_id'], 'Hello There @brucewayne, @tonystark, @natasharomanoff', later_time)

    time.sleep(2)

    # Get each user's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user3_notifications = th.notifications_get(user3['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()
    user3_notifications = user3_notifications.json()

    # Check that user1 was tagged
    assert user1_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, natasharomanoff, tonystark: Hello There @brucewa"
        },
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "natasharomanoff tagged you in Cat lovers: Hello There @brucewa"
        },
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark added you to brucewayne, natasharomanoff, tonystark"
        }
    ]

    # Check that user2 was tagged
    assert user2_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, natasharomanoff, tonystark: Hello There @brucewa"
        },
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "natasharomanoff tagged you in Cat lovers: Hello There @brucewa"
        }
    ]

    # Check that user3 was tagged
    assert user3_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, natasharomanoff, tonystark: Hello There @brucewa"
        },
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "natasharomanoff tagged you in Cat lovers: Hello There @brucewa"
        },
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark added you to brucewayne, natasharomanoff, tonystark"
        }
    ]

# Test that a user only gets 1 notification when they are tagged multiple times
# in a message
def test_notifications_same_user_tagged_multiple_times_in_message(clear_data):
    
    # Register 2 users
    user1 = th.auth_register("batman@gmail.com", "password", "bruce", "wayne")
    user2 = th.auth_register("ironman@gmail.com", "1235678", "tony", "stark")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates a channel and user2 joins
    channel = th.channels_create(user1['token'], "CAMELS", True)
    channel = channel.json()
    th.channel_join(user2['token'], channel['channel_id'])

    # User1 creates a dm with user2
    dm = th.dm_create(user1['token'], [user2['auth_user_id']])
    dm = dm.json()

    # User1 sends a single message in channel tagging user2 multiple times
    th.message_send(user1['token'], channel['channel_id'], "@tonystark@tonystark @tonystark@tonystark @tonystark!!!!!")

    # User2 sends a single message in teh dm tagging user1  multiple times
    th.message_senddm(user2['token'], dm['dm_id'], " @brucewayne @brucewayne@brucewayne @brucewayne @brucewayne!!!")

    # Get each user's notifications
    user1_notifications = th.notifications_get(user1['token'])

    user2_notifications = th.notifications_get(user2['token'])

    user1_notifications = user1_notifications.json()
    user2_notifications = user2_notifications.json()

    # Check that each user only received one notification even though they were
    # tagged multiple times in a single message
    assert user1_notifications['notifications'] == [ 
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "tonystark tagged you in brucewayne, tonystark:  @brucewayne @brucew"
        }
    ]

    assert user2_notifications['notifications'] == [ 
        {
           'channel_id': channel['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne tagged you in CAMELS: @tonystark@tonystark"
        },
        {
           'channel_id': -1,
           'dm_id': dm['dm_id'],
           'notification_message': "brucewayne added you to brucewayne, tonystark"
        }
    ]

# Check that notifications are in right order if user calls notifications twice
def tests_notifications_order(clear_data):

    # Register 2 users
    user1 = th.auth_register("batman@gmail.com", "password", "bruce", "wayne")
    user2 = th.auth_register("ironman@gmail.com", "1235678", "tony", "stark")

    user1 = user1.json()
    user2 = user2.json()

    # User1 creates 2 channels and invites user2 to both
    channel1 = th.channels_create(user1['token'], "CAMELS", True)
    channel2 = th.channels_create(user1['token'], "GOATS", True)
    
    channel1 = channel1.json()
    channel2 = channel2.json()

    th.channel_invite(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    th.channel_invite(user1['token'], channel2['channel_id'], user2['auth_user_id'])

    # Get user2 notifications
    user2_notifications1 = th.notifications_get(user2['token'])
    
    user2_notifications1 = user2_notifications1.json()

    # Check that notifications are correct
    assert user2_notifications1['notifications'] == [ 
        {
           'channel_id': channel2['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne added you to GOATS"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne added you to CAMELS"
        }
    ]

    # User1 sends 2 messages in channels tagging user2
    th.message_send(user1['token'], channel1['channel_id'], "@tonystark")
    th.message_send(user1['token'], channel2['channel_id'], "hello @tonystark")

    # Get user2 notifications again
    user2_notifications2 = th.notifications_get(user2['token'])
    
    user2_notifications2 = user2_notifications2.json()

    # Check order of notifications is correct
    assert user2_notifications2['notifications'] == [ 
        {
            'channel_id': channel2['channel_id'],
            'dm_id': -1,
            'notification_message': "brucewayne tagged you in GOATS: hello @tonystark"
        },
        {
            'channel_id': channel1['channel_id'],
            'dm_id': -1,
            'notification_message': "brucewayne tagged you in CAMELS: @tonystark"
        },
        {
           'channel_id': channel2['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne added you to GOATS"
        },
        {
           'channel_id': channel1['channel_id'],
           'dm_id': -1,
           'notification_message': "brucewayne added you to CAMELS"
        }
    ] 
