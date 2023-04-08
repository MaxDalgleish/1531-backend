import pytest
import requests
from src import config
from tests.test_helpers import invalid_token4

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
def get_channel_detail(token, channel_id):

    detail_response = requests.get(config.url + "/channel/details/v2",
                                   params={'token': token, 'channel_id': channel_id})
    
    return detail_response.json()

######################################### TESTING BEGINS #########################################

# Test for invalid token and returning AccessError
def test_user_profile_sethandle_v1_invalid_token(clear):
    
    requests.post(config.url + "auth/register/v2",
                    json={'email': 'test1@gmail.com',
                        'password': 'password',
                        'name_first': 'John', 
                        'name_last': 'Doe'})

    handle_response = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': invalid_token4(), 
                                          'handle_str': 'newidentity'})
    
    assert handle_response.status_code == 403
    
# Test when handle is not between 3 to 20 characters InputError is returned
def test_user_profile_sethandle_v1_incorrect_length(clear):

    reg_response = create_user1()

    handle_response1 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response['token'], 
                                          'handle_str': 'pp'})
    
    handle_response2 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response['token'], 
                                          'handle_str': 'ppasdfasdfasdffasdfasdfasdf'})

    assert handle_response1.status_code == 400
    assert handle_response2.status_code == 400
    
# Test when handle contains non-alphanumeric characters InputError is returned
def test_user_profile_sethandle_v1_non_alphanumeric(clear):

    reg_response = create_user1()
    
    handle_response = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response['token'], 
                                          'handle_str': 'inv@lid'})

    assert handle_response.status_code == 400
    
# Test when handle is a duplicate returning InputError
def test_user_profile_sethandle_v1_duplicate(clear):

    reg_response1 = create_user1()
    create_user2()

    handle_response = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response1['token'], 
                                          'handle_str': 'pikachuash'})

    assert handle_response.status_code == 400
    
# Test handle changing with only users registered
def test_user_profile_sethandle_v1_users(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()

    handle_response1 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response1['token'], 
                                          'handle_str': 'new'})

    handle_response2 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response2['token'], 
                                          'handle_str': 'whatsappistwentyisas'})                                          
    
    detail_response1 = create_user_profile(reg_response1['token'], reg_response1['auth_user_id'])
    detail_response2 = create_user_profile(reg_response2['token'], reg_response2['auth_user_id'])

    assert handle_response1.status_code == 200
    assert handle_response2.status_code == 200
    assert detail_response1['user']['handle_str'] == 'new'
    assert detail_response2['user']['handle_str'] == 'whatsappistwentyisas'

# Test handle changing with channels created
def test_user_profile_sethandle_v1_channels(clear):

    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    channel_response1 = create_channel1(reg_response1)
    channel_response2 = create_channel2(reg_response2)

    # User 3 joining Channel 2
    requests.post(config.url + "channel/join/v2",
            json={'token': reg_response3['token'], 
                'channel_id': channel_response2['channel_id']})
    
    # User 1 inviting User 2 to Channel 1
    requests.post(config.url + 'channel/invite/v2',
            json={'token': reg_response1['token'],
                    'channel_id': channel_response1['channel_id'],
                    'u_id': reg_response2['auth_user_id']})
    
    handle_response1 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response1['token'], 
                                          'handle_str': 'newidentity'})

    handle_response2 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response2['token'], 
                                          'handle_str': 'whatsapp'})  

    handle_response3 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response3['token'], 
                                          'handle_str': 'hodl'}) 

    channel_detail1 = get_channel_detail(reg_response1['token'], channel_response1['channel_id'])
    channel_detail2 = get_channel_detail(reg_response2['token'], channel_response2['channel_id'])

    assert handle_response1.status_code == 200
    assert handle_response2.status_code == 200
    assert handle_response3.status_code == 200
    assert channel_detail1['all_members'][0]['handle_str'] == 'newidentity'
    assert channel_detail1['all_members'][1]['handle_str'] == 'whatsapp'
    assert channel_detail2['all_members'][0]['handle_str'] == 'whatsapp'
    assert channel_detail2['all_members'][1]['handle_str'] == 'hodl'
    assert channel_detail1['owner_members'][0]['handle_str'] == 'newidentity'
    assert channel_detail2['owner_members'][0]['handle_str'] == 'whatsapp'

# Test handle changing with dms created
def test_user_profile_sethandle_v1_dms(clear):
    
    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response1['token'],
                                      "u_ids": [2, 3]})

    dm_response = dm_response.json()

    handle_response1 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response1['token'], 
                                          'handle_str': 'newidentity'})

    handle_response2 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response2['token'], 
                                          'handle_str': 'whatsapp'})  

    handle_response3 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response3['token'], 
                                          'handle_str': 'hodl'}) 

    dm_detail_response = requests.get(config.url + 'dm/details/v1',
                                   params={'token': reg_response1['token'],
                                           'dm_id': dm_response['dm_id']})

    dm_detail_response = dm_detail_response.json()   

    assert handle_response1.status_code == 200
    assert handle_response2.status_code == 200
    assert handle_response3.status_code == 200
    assert dm_detail_response['members'][0]['handle_str'] == 'newidentity'
    assert dm_detail_response['members'][1]['handle_str'] == 'whatsapp'
    assert dm_detail_response['members'][2]['handle_str'] == 'hodl'
    
# Test handle changing with dms and channels created
def test_user_profile_sethandle_v1_mixed(clear):

    reg_response1 = create_user1()
    reg_response2 = create_user2()
    reg_response3 = create_user3()
    
    channel_response1 = create_channel1(reg_response1)
    channel_response2 = create_channel2(reg_response2)

    # User 3 joining Channel 2
    requests.post(config.url + "channel/join/v2",
            json={'token': reg_response3['token'], 
                'channel_id': channel_response2['channel_id']})
    
    # User 1 inviting User 2 to Channel 1
    requests.post(config.url + 'channel/invite/v2',
            json={'token': reg_response1['token'],
                    'channel_id': channel_response1['channel_id'],
                    'u_id': reg_response2['auth_user_id']})

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response1['token'],
                                      "u_ids": [2, 3]})

    dm_response = dm_response.json()

    handle_response1 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response1['token'], 
                                          'handle_str': 'newidentity'})

    handle_response2 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response2['token'], 
                                          'handle_str': 'whatsapp'})  

    handle_response3 = requests.put(config.url + 'user/profile/sethandle/v1',
                                    json={'token': reg_response3['token'], 
                                          'handle_str': 'hodl'}) 

    dm_detail_response = requests.get(config.url + 'dm/details/v1',
                                   params={'token': reg_response1['token'],
                                           'dm_id': dm_response['dm_id']})

    dm_detail_response = dm_detail_response.json()   
                                      
    channel_detail1 = get_channel_detail(reg_response1['token'], channel_response1['channel_id'])
    channel_detail2 = get_channel_detail(reg_response2['token'], channel_response2['channel_id'])

    assert handle_response1.status_code == 200
    assert handle_response2.status_code == 200
    assert handle_response3.status_code == 200
    assert dm_detail_response['members'][0]['handle_str'] == 'newidentity'
    assert dm_detail_response['members'][1]['handle_str'] == 'whatsapp'
    assert dm_detail_response['members'][2]['handle_str'] == 'hodl'
    assert channel_detail1['all_members'][0]['handle_str'] == 'newidentity'
    assert channel_detail1['all_members'][1]['handle_str'] == 'whatsapp'
    assert channel_detail2['all_members'][0]['handle_str'] == 'whatsapp'
    assert channel_detail2['all_members'][1]['handle_str'] == 'hodl'
    assert channel_detail1['owner_members'][0]['handle_str'] == 'newidentity'
    assert channel_detail2['owner_members'][0]['handle_str'] == 'whatsapp'                                          