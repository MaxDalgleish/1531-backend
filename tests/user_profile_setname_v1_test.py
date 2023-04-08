import pytest
import requests
from src import config
from tests.test_helpers import invalid_token2

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

# Registering user two
def create_user2():

    # Register a user
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test2@gmail.com',
                        'password': 'validresponse',
                        'name_first': 'Pikachu', 
                        'name_last': 'Ash'})

    return reg_response.json()

# Registering user three
def create_user3():

    # Register a user
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test3@gmail.com',
                        'password': 'testing',
                        'name_first': 'Good', 
                        'name_last': 'Day'})

    return reg_response.json()

# Creating channel 1
def create_channel1(reg_response):

    # Create a channel
    channel_response = requests.post(config.url + "/channels/create/v2",
                                     json={"token": reg_response["token"],
                                           "name": "Channel 1",
                                           'is_public': True})

    return channel_response.json()             

# Creating channel 2
def create_channel2(reg_response):

    # Create a channel
    channel_response = requests.post(config.url + "/channels/create/v2",
                                     json={"token": reg_response["token"],
                                           "name": "Channel 2",
                                           'is_public': True})

    return channel_response.json()                                       

# Retreieve user profile
def create_user_profile(token, u_id):

    user_response = requests.get(config.url + "user/profile/v1",
                                  params={"token": token, 
                                          "u_id": u_id})
    
    return user_response.json()

# Create dm
def create_dm(reg_response, u_ids):

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response['token'],
                                      "u_ids": u_ids})

    return dm_response.json()                                  

# Retreieve channel details
def create_channel_detail(token, channel_id):

    detail_response = requests.get(config.url + "/channel/details/v2",
                                   params={'token': token, 'channel_id': channel_id})
    
    return detail_response.json()

######################################### TESTING BEGINS #########################################

# Test for invalid token and returning AccessError
def test_user_profile_setname_v1_invalid_token(clear):
    
    requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': invalid_token2(), 
                                          'name_first': 'Clark', 
                                          'name_last': 'Kent'})
    
    assert setname_response.status_code == 403

# Test for giving invalid over 50 chars length of first_name and last name and returning InputError
def test_user_profile_setname_v1_over_length(clear):
    reg_response = create_user1()

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': "soireallythinkthatjokerandalltheothervillansmadeagoodpointaboutbatmansprinciples", 
                                          'name_last': "Batman"})

    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': "Batman", 
                                          'name_last': "soireallythinkthatjokerandalltheothervillansmadeagoodpointaboutbatmansprinciplesBatman"})

    assert setname_response1.status_code == 400
    assert setname_response2.status_code == 400

# Test for giving empty first name and last_name and returning InputError
def test_user_profile_setname_v1_empty(clear):
    
    reg_response = create_user1()

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': '', 
                                          'name_last': 'Tom'})
    
    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': 'Tom', 
                                          'name_last': ''})

    assert setname_response1.status_code == 400
    assert setname_response2.status_code == 400

# Test for non-alphanumeric characters inside the inputs
def test_user_profile_setname_v1_non_alphanumeric(clear):
    
    reg_response = create_user1()

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': '$@r@h', 
                                          'name_last': "(..)"})
    
    profile_response = create_user_profile(reg_response['token'], 
                                           reg_response['auth_user_id'])
    
    assert profile_response['user']['name_first'] == '$@r@h'
    assert profile_response['user']['name_last'] == "(..)"
    assert setname_response.status_code == 200

# ASSUMPTION: User will always give a value for name_first or name_last

# Test for changing first name 
def test_user_profile_setname_v1_firstname(clear):
    
    reg_response = create_user1()

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token':  reg_response['token'], 
                                          'name_first': 'New',
                                           "name_last": 'Doe'})

    profile_response = create_user_profile(reg_response['token'], 
                                           reg_response['auth_user_id'])

    assert profile_response['user']['name_first'] == 'New'
    assert profile_response['user']['name_last'] == "Doe"
    assert setname_response.status_code == 200
    
# Test for changing last name
def test_user_profile_setname_v1_lastname(clear):
    
    reg_response = create_user1()

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': "John", 
                                          'name_last': 'New'})
    
    profile_response = create_user_profile(reg_response['token'], 
                                           reg_response['auth_user_id'])

    assert profile_response['user']['name_first'] == 'John'
    assert profile_response['user']['name_last'] == "New"
    assert setname_response.status_code == 200
    
# Test for changing both first and last name
def test_user_profile_setname_v1_both_names(clear):
    
    reg_response = create_user1()

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': 'Witness', 
                                          'name_last': 'Protection'})
    
    profile_response = create_user_profile(reg_response['token'], 
                                           reg_response['auth_user_id'])

    assert profile_response['user']['name_first'] == 'Witness'
    assert profile_response['user']['name_last'] == "Protection"
    assert setname_response.status_code == 200
    
# Test for changing names multiple times
def test_user_profile_setname_v1_change_multiple_times(clear):
    
    reg_response = create_user1()

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': 'New', 
                                          'name_last': 'Name'})
                                        
    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': 'Jason', 
                                          'name_last': 'Bourne'})

    profile_response = create_user_profile(reg_response['token'], 
                                           reg_response['auth_user_id'])

    assert profile_response['user']['name_first'] == 'Jason'
    assert profile_response['user']['name_last'] == "Bourne"
    assert setname_response1.status_code == 200
    assert setname_response2.status_code == 200
    
# Test for multiple users changing names
def test_user_profile_setname_v1_multiple_users(clear):
    
    reg_response1 = create_user1()

    reg_response2 = create_user2()

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response1['token'], 
                                          'name_first': "Mike", 
                                          'name_last': "Tyson"})
    
    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response2['token'], 
                                          'name_first': "Kanye", 
                                          'name_last': 'West'})

    profile_response1 = create_user_profile(reg_response1['token'], 
                                           reg_response1['auth_user_id'])

    profile_response2 = create_user_profile(reg_response2['token'], 
                                           reg_response2['auth_user_id'])
    
    assert profile_response1['user']['name_first'] == 'Mike'
    assert profile_response1['user']['name_last'] == "Tyson"
    assert profile_response2['user']['name_first'] == 'Kanye'
    assert profile_response2['user']['name_last'] == "West"
    assert setname_response1.status_code == 200
    assert setname_response2.status_code == 200

# Testing with one user creating a channel
def test_user_profile_setname_v1_channel(clear):
    
    reg_response = requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                          'password': 'password',
                          'name_first': 'John', 
                          'name_last': 'Doe'})
    
    reg_response = reg_response.json()

    channel_response = requests.post(config.url + "/channels/create/v2",
                                     json={"token": reg_response["token"],
                                           "name": "Channel 1",
                                           'is_public': True})

    channel_response = channel_response.json()

    setname_response = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response['token'], 
                                          'name_first': "Mike", 
                                          'name_last': "Tyson"})

    detail_response = requests.get(config.url + 'channel/details/v2',
                                   params={"token": reg_response['token'],
                                         'channel_id': channel_response['channel_id']})                                      

    detail_response = detail_response.json()

    assert setname_response.status_code == 200
    assert detail_response['all_members'][0]['name_first'] == "Mike"
    assert detail_response['all_members'][0]['name_last'] == "Tyson"
    assert detail_response['owner_members'][0]['name_first'] == "Mike"
    assert detail_response['owner_members'][0]['name_last'] == "Tyson"

# Testing with users creating channels
def test_user_profile_setname_v1_channels(clear):

    reg_response1 = create_user1()
    reg_response2 = create_user2()

    channel_response1 = create_channel1(reg_response1)
    channel_response2 = create_channel2(reg_response2)


    requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response1['token'], 
                                          'name_first': "L@bron", 
                                          'name_last': "J@mes"})
    
    requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response2['token'], 
                                          'name_first': "W", 
                                          'name_last': "C"})

    detail_response1 = create_channel_detail(reg_response1['token'], channel_response1['channel_id'])
    detail_response2 = create_channel_detail(reg_response2['token'], channel_response2['channel_id'])

    assert detail_response1['all_members'][0]['name_first'] == "L@bron"
    assert detail_response1['all_members'][0]['name_last'] == "J@mes"
    assert detail_response2['all_members'][0]['name_first'] == "W"
    assert detail_response2['all_members'][0]['name_last'] == "C"
    assert detail_response1['owner_members'][0]['name_first'] == "L@bron"
    assert detail_response1['owner_members'][0]['name_last'] == "J@mes"
    assert detail_response2['owner_members'][0]['name_first'] == "W"
    assert detail_response2['owner_members'][0]['name_last'] == "C"

# Testing with users inviting and joining channels
def test_user_profile_setname_v1_invite_join_channels(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()

    channel_response1 = create_channel1(reg_response1)
    channel_response2 = create_channel2(reg_response2)

    # User 1 joining Channel 2
    requests.post(config.url + "channel/join/v2",
            json={'token': reg_response1['token'], 
                'channel_id': channel_response2['channel_id']})
    
    # User 1 inviting User 2 to Channel 1
    requests.post(config.url + 'channel/invite/v2',
            json={'token': reg_response1['token'],
                    'channel_id': channel_response1['channel_id'],
                    'u_id': 2})

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response1['token'], 
                                          'name_first': "Mike", 
                                          'name_last': "Tyson"})

    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response2['token'], 
                                          'name_first': "Kanye", 
                                          'name_last': 'West'})

    detail_response1 = create_channel_detail(reg_response1['token'], channel_response1['channel_id'])
    detail_response2 = create_channel_detail(reg_response2['token'], channel_response2['channel_id'])
    
    assert setname_response1.status_code == 200
    assert setname_response2.status_code == 200
    assert detail_response1['all_members'][1]["name_first"] == "Kanye"  
    assert detail_response1['all_members'][1]["name_last"] == "West"    
    assert detail_response2['all_members'][1]["name_first"] == "Mike"  
    assert detail_response2['all_members'][1]["name_last"] == "Tyson"
    assert detail_response1['owner_members'][0]['name_first'] == "Mike"
    assert detail_response1['owner_members'][0]['name_last'] == "Tyson"
    assert detail_response2['owner_members'][0]['name_first'] == "Kanye"
    assert detail_response2['owner_members'][0]['name_last'] == "West"
                                      
# Testing with users creating dms
def test_user_profile_setname_v1_dms(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response1['token'],
                                      "u_ids": [2, 3]})

    dm_response = dm_response.json()

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response1['token'], 
                                          'name_first': "Mike", 
                                          'name_last': "Tyson"})

    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response2['token'], 
                                          'name_first': "Kanye", 
                                          'name_last': 'West'})  

    setname_response3 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response3['token'], 
                                          'name_first': "The", 
                                          'name_last': 'Office'})    
    
    dm_detail_response = requests.get(config.url + 'dm/details/v1',
                                   params={'token': reg_response1['token'],
                                           'dm_id': dm_response['dm_id']})

    dm_detail_response = dm_detail_response.json()                       

    assert dm_detail_response['members'][0]['name_first'] == "Mike"
    assert dm_detail_response['members'][0]['name_last'] == "Tyson"
    assert dm_detail_response['members'][1]['name_first'] == "Kanye"
    assert dm_detail_response['members'][1]['name_last'] == "West"
    assert dm_detail_response['members'][2]['name_first'] == "The"
    assert dm_detail_response['members'][2]['name_last'] == "Office"
    assert setname_response1.status_code == 200
    assert setname_response2.status_code == 200
    assert setname_response3.status_code == 200                                                                                                                                               

# Testing with users creating channels and dms
def test_user_profile_setname_v1_channels_and_dms(clear):

    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response1['token'],
                                      "u_ids": [2, 3]})

    dm_response = dm_response.json()

    channel_response1 = create_channel1(reg_response1)
    channel_response2 = create_channel2(reg_response2)

    # User 1 joining Channel 2
    requests.post(config.url + "channel/join/v2",
            json={'token': reg_response1['token'], 
                'channel_id': channel_response2['channel_id']})
    
    # User 1 inviting User 2 to Channel 1
    requests.post(config.url + 'channel/invite/v2',
            json={'token': reg_response1['token'],
                    'channel_id': channel_response1['channel_id'],
                    'u_id': 2})
    
    # User 3 joining Channel 2
    requests.post(config.url + "channel/join/v2",
            json={'token': reg_response3['token'], 
                'channel_id': channel_response2['channel_id']})

    setname_response1 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response1['token'], 
                                          'name_first': "Mike", 
                                          'name_last': "Tyson"})

    setname_response2 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response2['token'], 
                                          'name_first': "Kanye", 
                                          'name_last': 'West'})  

    setname_response3 = requests.put(config.url + 'user/profile/setname/v1',
                                    json={'token': reg_response3['token'], 
                                          'name_first': "The", 
                                          'name_last': 'Office'})   

    dm_detail_response = requests.get(config.url + 'dm/details/v1',
                                   params={'token': reg_response1['token'],
                                           'dm_id': dm_response['dm_id']})

    detail_response1 = create_channel_detail(reg_response1['token'], channel_response1['channel_id'])
    detail_response2 = create_channel_detail(reg_response2['token'], channel_response2['channel_id'])

    dm_detail_response = dm_detail_response.json()   

    assert setname_response1.status_code == 200
    assert setname_response2.status_code == 200
    assert setname_response3.status_code == 200
    assert detail_response1['all_members'][1]["name_first"] == "Kanye"  
    assert detail_response1['all_members'][1]["name_last"] == "West"    
    assert detail_response2['all_members'][1]["name_first"] == "Mike"  
    assert detail_response2['all_members'][1]["name_last"] == "Tyson"
    assert detail_response1['owner_members'][0]['name_first'] == "Mike"
    assert detail_response1['owner_members'][0]['name_last'] == "Tyson"
    assert detail_response2['owner_members'][0]['name_first'] == "Kanye"
    assert detail_response2['owner_members'][0]['name_last'] == "West"
    assert dm_detail_response['members'][0]['name_first'] == "Mike"
    assert dm_detail_response['members'][0]['name_last'] == "Tyson"
    assert dm_detail_response['members'][1]['name_first'] == "Kanye"
    assert dm_detail_response['members'][1]['name_last'] == "West"
    assert dm_detail_response['members'][2]['name_first'] == "The"
    assert dm_detail_response['members'][2]['name_last'] == "Office"  
