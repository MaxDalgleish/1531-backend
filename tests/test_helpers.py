import requests
from src import config

# Generate invalid token1
def invalid_token1():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "hyunseo@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Justin",
                                            "name_last": "Son"})
    register_response = register_response.json()

    # Log user out so that their token is invalidated
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_response['token']})

    return register_response['token']

# Generate invalid token2
def invalid_token2():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "brian@gmail.com",
                                            "password": "validpassword123",
                                            "name_first": "Brian",
                                            "name_last": "Li"})
    register_response = register_response.json()

    # Log user out so that their token is invalidated
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_response['token']})

    return register_response['token']


# Generate invalid token3
def invalid_token3():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "helloworld@gmail.com",
                                            "password": "password123",
                                            "name_first": "Harry",
                                            "name_last": "Potter"})
    register_response = register_response.json()

    # Log user out so that their token is invalidated
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_response['token']})

    return register_response['token']

# Generate invalid token4
def invalid_token4():
    
    # Register a user and save response
    register_response = requests.post(config.url + "auth/register/v2",
                                      json={"email": "Allan@gmail.com",
                                            "password": "987654321",
                                            "name_first": "Allan",
                                            "name_last": "Zhang"})
    register_response = register_response.json()

    # Log user out so that their token is invalidated
    requests.post(config.url + "auth/logout/v1",
                  json={"token": register_response['token']})

    return register_response['token']

# Sends request to register user and returns response
def request_register(email, password, name_first, name_last):
     
     return requests.post(config.url + "auth/register/v2", 
                          json={'email': email,
                                'password': password,
                                'name_first': name_first, 
                                'name_last': name_last})

def request_channels_create(token, name, is_public):
    
    return requests.post(config.url + "channels/create/v2", 
                          json={'token': token,
                                'name': name,
                                'is_public': is_public})

def request_channel_invite(token, channel_id, u_id):
    
    return requests.post(config.url + "channel/invite/v2", 
                          json={'token': token,
                                'channel_id': channel_id,
                                'u_id': u_id})

def request_dm_create(token, u_ids):
    
    return requests.post(config.url + "dm/create/v1", 
                          json={'token': token,
                                'u_ids': u_ids})

def request_message_send(token, channel_id, message):

    return requests.post(config.url + "message/send/v1",
                                 json={'token': token,
                                       'channel_id': channel_id,
                                       'message': message})

def request_message_senddm(token, dm_id, message):
    return requests.post(config.url + "message/senddm/v1",
                         json={'token': token,
                               'dm_id': dm_id,
                               'message': message})

def request_message_remove(token, message_id):
    return requests.delete(config.url + "message/remove/v1",
                           json={'token': token,
                                 'message_id': message_id})

def request_message_edit(token, message_id, message):
    return requests.put(config.url + "message/edit/v1",
                         json={'token': token,
                               'message_id': message_id,
                               'message': message})

def request_message_share(token, og_message_id, message, channel_id, dm_id):
    return requests.post(config.url + "message/share/v1",
                         json={'token': token,
                               'og_message_id': og_message_id,
                               'message': message,
                               'channel_id': channel_id,
                               'dm_id': dm_id})

# Sends request for user/stats/v1 and returns response
def request_user_stats(token):

    return requests.get(config.url + "user/stats/v1",
                        params={'token': token})

# Sends request for users/stats/v1 and returns response
def request_users_stats(token):

    return requests.get(config.url + "users/stats/v1",
                        params={'token': token})

def request_channel_join(token, channel_id):

    return requests.post(config.url + "channel/join/v2", 
                         json = {'token': token, "channel_id": channel_id})

def request_remove_user(token, u_id):

    return requests.delete(config.url + "admin/user/remove/v1",
                           json={'token': token, "u_id": u_id})

def request_user_profile(token, u_id):

    return requests.get(config.url + "user/profile/v1",
                        params={'token': token,
                                'u_id': u_id})

def request_message_react(token, message_id, react_id):

    return requests.post(config.url + "message/react/v1",
                        json={'token': token,
                              'message_id': message_id,
                              'react_id': react_id})
     
def request_login(email, password):
     
     return requests.post(config.url + "auth/login/v2", 
                          json={'email': email,
                                'password': password})
    
def request_channel_details(token, channel_id):
    
    return requests.get(config.url + "channel/details/v2",
                        params={"token": token,
                                "channel_id": channel_id})

def request_dm_remove(token, dm_id):
    return requests.delete(config.url + "dm/remove/v1",
                           json={'token': token,
                                 'dm_id': dm_id})
    
def request_react(token, message_id, react_id):
    
    return requests.post(config.url + "message/react/v1",
                         json={ "token": token,
                                "message_id": message_id,
                                "react_id": react_id}) 

def request_dm_leave(token, dm_id):
    
    return requests.post(config.url + "dm/leave/v1",
                         json={'token': token,
                               'dm_id': dm_id})

def request_channel_leave(token, channel_id):

    return requests.post(config.url + "channel/leave/v1",
                         json={'token': token,
                               'channel_id': channel_id})
    
def request_message_sendlater(token, channel_id, message, time_sent):
    return requests.post(config.url + "message/sendlater/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message,
                               'time_sent': time_sent})
    
def request_message_sendlaterdm(token, dm_id, message, time_sent):
    return requests.post(config.url + 'message/sendlaterdm/v1',
                         json={'token': token,
                               'dm_id': dm_id,
                               'message': message,
                               'time_sent': time_sent})
    
def create_user1():

    # Register a user
    return requests.post(config.url + "auth/register/v2",
                        json={'email': 'derrick@gmail.com',
                            'password': '123456',
                            'name_first': 'Derrick', 
                            'name_last': 'Doan'})

def create_user2():

    # Register a user
    return requests.post(config.url + "auth/register/v2",
                        json={'email': 'cynthia@gmail.com',
                            'password': '123456',
                            'name_first': 'Cynthia', 
                            'name_last': 'Li'})

def create_user3():

    # Register a user
    return requests.post(config.url + "auth/register/v2",
                        json={'email': 'justin@gmail.com',
                            'password': '123456',
                            'name_first': 'Justin', 
                            'name_last': 'Son'})

def create_channel1(reg_response):

    # Create a channel
    return requests.post(config.url + "/channels/create/v2",
                                     json={"token": reg_response["token"],
                                           "name": "Channel 1",
                                           'is_public': True})

def create_dm1(reg_response, u_ids):

    return requests.post(config.url + "/dm/create/v1",
                                json={"token": reg_response['token'],
                                      "u_ids": u_ids})

def send_message_in_channel_1(reg_response, channel_response):

    return requests.post(config.url + "message/send/v1",
				  json={'token': reg_response['token'],
						'channel_id': channel_response['channel_id'],
						'message': "The first lecture will be on Wednesday 10am"})

def react_to_message(reg_response, message_response, react_id):

    return requests.post(config.url + "message/react/v1",
                            json={"token": reg_response["token"],
                                  "message_id": message_response["message_id"],
                                  "react_id": react_id}) 

def send_message_in_dm_1(user, dm):

    return requests.post(config.url + "message/senddm/v1",
				  json={'token': user['token'],
						'dm_id': dm['dm_id'],
						'message': "Welcome to COMP1531"})

def thumbs_up_react_id():

    return 1

def get_channel_messages(token, channel_id, start):

    return requests.get(config.url + 'channel/messages/v2',
                    params={'token': token,
                            'channel_id': channel_id,
                            'start': start})

def get_dm_messages(token, dm_id, start):
    
    return requests.get(config.url + "dm/messages/v1", 
                    params={'token': token,
                            'dm_id': dm_id,
                            'start': start})

def unreact_to_message(reg_response, message_response, react_id):

    return requests.post(config.url + "message/unreact/v1",
                         json={ "token": reg_response["token"],
                                "message_id": message_response["message_id"],
                                "react_id": react_id,}) 
    

def leave_channel(reg_response, channel_response):
    return requests.post(config.url + 'channel/leave/v1',
                         json = {'token': reg_response['token'],
                                 'channel_id': channel_response['channel_id']})

def join_channel(reg_response, channel_response):
    return requests.post(config.url + 'channel/join/v2',
                                 json={'token': reg_response['token'],
                                       'channel_id': channel_response['channel_id']})
    

def leave_dm(reg_response, dm_response):
    return requests.post(config.url + "dm/leave/v1",
                                   json={'token': reg_response['token'],
                                         'dm_id': dm_response['dm_id']})

def passwordreset_request(email):

    return requests.post(config.url + 'auth/passwordreset/request/v1',
                         json={'email': email})

def request_start_standup(token, channel_id, length):
    return requests.post(config.url + "standup/start/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'length': length})

def request_active_standup(token, channel_id):
    return requests.get(config.url + "standup/active/v1",
                        params={'token': token,
                                'channel_id': channel_id})

def request_send_standup(token, channel_id, message):    
    return requests.post(config.url + "standup/send/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message})

############################ FUNCTIONS FOR TEST REQUESTS ############################

def auth_login(email, password):
    return requests.post(config.url + "auth/login/v2", 
                         json={'email': email,
                               'password': password})

def auth_register(email, password, name_first, name_last):
    return requests.post(config.url + "auth/register/v2", 
                         json={'email': email,
                               'password': password,
                               'name_first': name_first, 
                               'name_last': name_last}) 

def auth_logout(token):
    return requests.post(config.url + "auth/logout/v1",
                         json={"token": token})

def channels_create(token, name, is_public):
    return requests.post(config.url + "channels/create/v2", 
                         json={'token': token,
                               'name': name,
                               'is_public': is_public})                       

def channels_list(token):
    return requests.get(config.url + "channels/list/v2",
                        params={'token': token})

def channels_listall(token):
    return requests.get(config.url + "channels/listall/v2",
                        params={'token': token})

def channel_details(token, channel_id):  
    return requests.get(config.url + "channel/details/v2",
                        params={'token': token,
                                'channel_id': channel_id})

def channel_join(token, channel_id):
    return requests.post(config.url + "channel/join/v2", 
                         json={'token': token,
                               'channel_id': channel_id})   

def channel_invite(token, channel_id, u_id):
    return requests.post(config.url + "channel/invite/v2", 
                         json={'token': token,
                               'channel_id': channel_id,
                               'u_id': u_id})

def channel_messages(token, channel_id, start):
    return requests.get(config.url + 'channel/messages/v2',
                        params={'token': token,
                                'channel_id': channel_id,
                                'start': start})

def channel_leave(token, channel_id):
    return requests.post(config.url + "channel/leave/v1",
                         json={'token': token,
                               'channel_id': channel_id})

def channel_add_owner(token, channel_id, u_id):
    return requests.post(config.url + 'channel/addowner/v1',
                         json={'token': token,
                               'channel_id': channel_id,
                               'u_id': u_id})

def channel_remove_owner(token, channel_id, u_id):
    return requests.post(config.url + 'channel/removeowner/v1',
                         json={'token': token,
                               'channel_id': channel_id,
                               'u_id': u_id})

def message_send(token, channel_id, message):
    return requests.post(config.url + "message/send/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message})

def message_edit(token, message_id, message):
    return requests.put(config.url + "message/edit/v1",
                         json={'token': token,
                               'message_id': message_id,
                               'message': message})

def message_remove(token, message_id):
    return requests.delete(config.url + "message/remove/v1",
                           json={'token': token,
                                 'message_id': message_id})

def dm_create(token, u_ids):
    return requests.post(config.url + "dm/create/v1", 
                         json={'token': token,
                               'u_ids': u_ids})

def dm_list(token):
    return requests.get(config.url + "dm/list/v1", 
                        params={'token': token})

def dm_remove(token, dm_id):
    return requests.delete(config.url + "dm/remove/v1",
                           json={'token': token,
                                 'dm_id': dm_id}) 

def dm_details(token, dm_id):
    return requests.get(config.url + "dm/details/v1",
                        params={'token': token,
                                'dm_id': dm_id})

def dm_leave(token, dm_id):
    return requests.post(config.url + "dm/leave/v1",
                         json={'token': token,
                               'dm_id': dm_id})

def dm_messages(token, dm_id, start):
    return requests.get(config.url + "dm/messages/v1", 
                        params={'token': token,
                                'dm_id': dm_id,
                                'start': start})

def message_senddm(token, dm_id, message):
    return requests.post(config.url + "message/senddm/v1",
                         json={'token': token,
                               'dm_id': dm_id,
                               'message': message})

def users_all(token):
    return requests.get(config.url + "users/all/v1",
                        params={'token': token})

def user_profile(token, u_id):
    return requests.get(config.url + "user/profile/v1",
                        params={'token': token,
                                'u_id': u_id})

def user_profile_setname(token, name_first, name_last):
    return requests.put(config.url + 'user/profile/setname/v1',
                        json={'token': token,
                              'name_first': name_first,
                              'name_last': name_last})

def user_profile_setemail(token, email):
    return requests.put(config.url + 'user/profile/setemail/v1',
                        json={'token': token, 
                              'email': email})

def user_profile_sethandle(token, handle_str):
    return requests.put(config.url + 'user/profile/sethandle/v1',
                        json={'token': token, 
                              'handle_str': 'handle_str'})

def admin_remove(token, u_id):
    return requests.delete(config.url + 'admin/user/remove/v1',
                           json={'token': token,
                                 'u_id': u_id})

def admin_change(token, u_id, permission_id):
    return requests.post(config.url + 'admin/userpermission/change/v1',
                         json={'token': token,
                               'u_id': u_id,
                               'permission_id': permission_id})

def clear():
    return requests.delete(config.url + "clear/v1")

def notifications_get(token):
    return requests.get(config.url + "notifications/get/v1",
                        params={'token': token})

def search(token, query_str):
    return requests.get(config.url + "search/v1",
                        params={'token': token,
                                'query_str': query_str})

def message_share(token, og_message_id, message, channel_id, dm_id):
    return requests.post(config.url + "message/share/v1",
                         json={'token': token,
                               'og_message_id': og_message_id,
                               'message': message,
                               'channel_id': channel_id,
                               'dm_id': dm_id})

def message_react(token, message_id, react_id):
    return requests.post(config.url + "message/react/v1",
                         json={'token': token,
                               'message_id': message_id,
                               'react_id': react_id})

def message_unreact(token, message_id, react_id):
    return requests.post(config.url + "message/unreact/v1",
                         json={'token': token,
                               'message_id': message_id,
                               'react_id': react_id})

def message_pin(token, message_id):
    return requests.post(config.url + "message/pin/v1",
                         json={'token': token,
                               'message_id': message_id})

def message_unpin(token, message_id):
    return requests.post(config.url + "message/unpin/v1",
                         json={'token': token,
                               'message_id': message_id})

def message_sendlater(token, channel_id, message, time_sent):
    return requests.post(config.url + "message/sendlater/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message,
                               'time_sent': time_sent})

def message_sendlaterdm(token, dm_id, message, time_sent):
    return requests.post(config.url + 'message/sendlaterdm/v1',
                         json={'token': token,
                               'dm_id': dm_id,
                               'message': message,
                               'time_sent': time_sent})

def start_standup(token, channel_id, length):
    return requests.post(config.url + "standup/start/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'length': length})

def active_standup(token, channel_id):
    return requests.get(config.url + "standup/active/v1",
                        params={'token': token,
                                'channel_id': channel_id})

def send_standup(token, channel_id, message):    
    return requests.post(config.url + "standup/send/v1",
                         json={'token': token,
                               'channel_id': channel_id,
                               'message': message})

def auth_passwordreset_request(email):
    return requests.post(config.url + 'auth/passwordreset/request/v1',
                         json={'email': email})

def auth_passwordreset_reset(reset_code, new_password):
    return requests.post(config.url + 'auth/passwordreset/reset/v1',
                         json={'reset_code': reset_code,
                               'new_password': new_password})

def user_upload_file(token, img_url, x_start, y_start, x_end, y_end):
    return requests.post(config.url + "user/profile/uploadphoto/v1",
                         json={'token': token,
                               'img_url': img_url,
                               'x_start': x_start,
                               'y_start': y_start,
                               'x_end': x_end,
                               'y_end': y_end})

def user_stats(token):
    return requests.get(config.url + "user/stats/v1",
                        params={'token': token})  

def users_stats(token):
    return requests.get(config.url + "users/stats/v1",
                        params={'token': token})
