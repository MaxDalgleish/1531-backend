import pytest
import requests
from src import config
from tests.test_helpers import invalid_token1

@pytest.fixture
def clear_data():
    requests.delete(config.url + "clear/v1")
    
def register_user_1():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'justin@gmail.com',
                                            'password': 'password123',
                                            'name_first': 'Justin', 
                                            'name_last': 'Son'})
    return register_response.json()

def register_user_2():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'cynthia@gmail.com',
                                            'password': 'password123456',
                                            'name_first': 'Cynthia', 
                                            'name_last': 'Li'})
    return register_response.json()

def register_user_3():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2", 
                                      json={'email': 'Derrick@gmail.com',
                                            'password': 'password000',
                                            'name_first': 'Derrick', 
                                            'name_last': 'Doan'})
    return register_response.json()

# Creating channel 1
def create_channel1(token):

    # Create a channel
    channel_response = requests.post(config.url + "/channels/create/v2",
                                     json={"token": token,
                                           "name": "Channel 1",
                                           'is_public': True})

    return channel_response.json()    

def create_dm(token, u_ids):

    dm_response = requests.post(config.url + "/dm/create/v1",
                                json={"token": token,
                                      "u_ids": u_ids})

    return dm_response.json()     

# Test if uploading photo with invalid token raises an AccessError
def test_user_uploadphoto_invalid_token(clear_data):

    # Register user 1
    register_user_1()
    
    # The user attempts to upload a photo with invalid token
    upload_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                   json={'token': invalid_token1(),
                                         'img_url': 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png',
                                         'x_start': 0,
                                         'y_start': 0,
                                         'x_end': 100,
                                         'y_end': 100})

    assert upload_response.status_code == 403
    
# Test if img url returns http status of anything other than 200
def test_user_uploadphoto_http_status(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']
    
    # The user attempts to upload a photo with invalid img url (https)
    url_response1 = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_960_720.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 100,
                                        'y_end': 100})


    url_response2 = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'https///////.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 100,
                                        'y_end': 100})

    url_response3 = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 100,
                                        'y_end': 100})


    assert url_response1.status_code == 400
    assert url_response2.status_code == 400
    assert url_response3.status_code == 400
    
# Test whether InputError is raised given invalid image dimensions
def test_user_uploadphoto_dimensions_invalid(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']
    
    # The user attempts to upload a photo with invalid dimensions
    share_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                   json={'token': token,
                                         'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                         'x_start': -1,
                                         'y_start': -1,
                                         'x_end': 160,
                                         'y_end': 201})

    assert share_response.status_code == 400
    
# Test whether InputError is raised given invalid image coordinates
def test_user_uploadphoto_dimensions_coordinates_invalid(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']
    
    # The user attempts to upload a photo with invalid coordinates
    share_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                   json={'token': token,
                                         'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                         'x_start': 100,
                                         'y_start': 100,
                                         'x_end': 50,
                                         'y_end': 50})

    assert share_response.status_code == 400
    
# Test if inputerror is raised given a non jpg file format
def test_user_uploadphoto_not_jpg(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']
    
    # The user attempts to upload a photo with invalid img url (website)
    url_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://info.cern.ch',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 100,
                                        'y_end': 100})

    assert url_response.status_code == 400

# Test if image can be uploaded successfully
def test_user_uploadphoto_success(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']

    register_user_2()
    
    url_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 120,
                                        'y_end': 120})

    user_response1 = requests.get(config.url + "user/profile/v1",
                                  params={"token": token, "u_id": 1})
    
    user_response1 = user_response1.json()

    assert user_response1['user']['profile_img_url'] == config.url + "static/user1.jpg"
    assert url_response.status_code == 200

# Test when the cropping dimensions are out of range
def test_user_uploadphoto_out_of_pixels(clear_data):
    
    # Register user 1
    user1 = register_user_1()
    token = user1['token']
    
    url_response = requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 9999999999,
                                        'y_end': 9999999999})

    user_response1 = requests.get(config.url + "user/profile/v1",
                                  params={"token": token, "u_id": 1})
    
    user_response1 = user_response1.json()

    assert user_response1['user']['profile_img_url'] == config.url + "static/default.jpg"
    assert url_response.status_code == 400

# Test if profile_img_url is updated inside the channels data
def test_user_uploadphoto_channel(clear_data):
    # Register user 1
    user1 = register_user_1()
    token = user1['token']

    user2 = register_user_2()
    token2 = user2['token']

    channel_response = create_channel1(token)

    requests.post(config.url + 'channel/join/v2',
                 json={'token': token2,
                       'channel_id': channel_response['channel_id']})

    requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 120,
                                        'y_end': 120})
    
    # Get channel details response
    details_response = requests.get(config.url + "channel/details/v2",
                                    params={'token': token,
                                            'channel_id': channel_response['channel_id']})
    details_response = details_response.json()
    
    assert details_response == {'name': 'Channel 1', 
                                'is_public': True, 
                                'owner_members': [{'u_id': 1, 
                                                'email': 'justin@gmail.com', 
                                                'name_first': 'Justin', 
                                                'name_last': 'Son', 
                                                'handle_str': 'justinson', 
                                                'profile_img_url': 'http://localhost:6123/static/user1.jpg'}], 
                                'all_members': [{'u_id': 1, 
                                                'email': 'justin@gmail.com', 
                                                'name_first': 'Justin', 
                                                'name_last': 'Son', 
                                                'handle_str': 'justinson', 
                                                'profile_img_url': 'http://localhost:6123/static/user1.jpg'},
                                               {'u_id': 2, 
                                               'email': 'cynthia@gmail.com', 
                                               'name_first': 'Cynthia', 
                                               'name_last': 'Li', 
                                               'handle_str': 'cynthiali', 
                                               'profile_img_url': 'http://localhost:6123/static/default.jpg'}]}

# Test if profile_img_url is updated inside the dms data
def test_user_uploadphoto_dm(clear_data):
    # Register user 1
    user1 = register_user_1()
    token = user1['token']

    user2 = register_user_2()
    token2 = user2['token']

    user3 = register_user_3()

    dm_response = create_dm(token2, [user1['auth_user_id'], user3['auth_user_id']])

    requests.post(config.url + "user/profile/uploadphoto/v1",
                                  json={'token': token,
                                        'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
                                        'x_start': 0,
                                        'y_start': 0,
                                        'x_end': 120,
                                        'y_end': 120})
    
    # Get channel details response
    details_response = requests.get(config.url + "dm/details/v1",
                                    params={'token': token,
                                            'dm_id': dm_response['dm_id']})
    details_response = details_response.json()

    assert details_response == {'name': 'cynthiali, derrickdoan, justinson', 
                                'members': [{'u_id': 2, 
                                             'email': 'cynthia@gmail.com', 
                                             'name_first': 'Cynthia', 
                                             'name_last': 'Li', 
                                             'handle_str': 'cynthiali', 
                                             'profile_img_url': 'http://localhost:6123/static/default.jpg'}, 
                                            {'u_id': 1, 
                                             'email': 'justin@gmail.com', 
                                             'name_first': 'Justin', 
                                             'name_last': 'Son', 
                                             'handle_str': 'justinson', 
                                             'profile_img_url': 'http://localhost:6123/static/user1.jpg'}, 
                                            {'u_id': 3, 
                                             'email': 'Derrick@gmail.com', 
                                             'name_first': 'Derrick', 
                                             'name_last': 'Doan', 
                                             'handle_str': 'derrickdoan', 
                                             'profile_img_url': 'http://localhost:6123/static/default.jpg'}]}