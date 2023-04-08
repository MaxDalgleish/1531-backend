import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src import config
from src.auth import auth_login_v1, \
                     auth_register_v1, \
                     auth_logout, \
                     auth_password_reset_request, \
                     auth_password_reset
from src.channel import channel_details_v1, \
                        channel_messages_v1, \
                        channel_join_v1, \
                        channel_invite_v1, \
                        channel_addowner_v1, \
                        channel_removeowner_v1, \
                        channel_leave_v1
from src.channels import channels_create_v1, \
                         channels_list_v1, \
                         channels_listall_v1
from src.message import message_send, \
                        message_senddm, \
                        message_remove, \
                        message_edit, \
                        message_react, \
                        message_unreact, \
                        message_pin, \
                        message_unpin, \
                        message_share, \
                        message_sendlater, \
                        message_sendlaterdm                    
from src.dm import dm_create, \
                   dm_list, \
                   dm_messages, \
                   dm_remove, \
                   dm_details, \
                   dm_leave
from src.users import users_all, \
                      user_profile, \
                      user_profile_setname, \
                      user_profile_setemail, \
                      user_profile_sethandle, \
                      user_stats, \
                      users_stats, \
                      user_profile_uploadphoto
from src.admin import admin_user_permission_change_v1, \
                      admin_user_remove_v1
from src.standup import standup_start, \
                        standup_active, \
                        standup_send
from src.notifications import get_notifications
from src.search import search
from src.other import clear_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path="/static")
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():

    # Gets the request body, turns it into json and stores it in request_data
    request_data = request.get_json()

    return dumps(auth_login_v1(request_data['email'],
                               request_data['password']))

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():

    # Gets the request body, turns it into json and stores it in request_data
    request_data = request.get_json()

    return dumps(auth_register_v1(request_data['email'], 
                                  request_data['password'],
                                  request_data['name_first'],
                                  request_data['name_last']))

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1():

    # Gets the request body, turns it into json and stores it in request_data
    request_data = request.get_json()
    
    return dumps(auth_logout(request_data['token']))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    
    # Gets the request body, turns it into json and stores it in request_data
    request_data = request.get_json()

    return dumps(channels_create_v1(request_data['token'], 
                                    request_data['name'],
                                    request_data['is_public']))

@APP.route("/channels/list/v2", methods=["GET"])
def channels_list_v2():

    # Gets the request body, turns it into json and stores it in request_data
    token = request.args.get("token")

    return dumps(channels_list_v1(token))

@APP.route("/channels/listall/v2", methods=["GET"])
def channels_listall_v2():
    
    # Get request_data from request
    token = request.args.get("token")

    return dumps(channels_listall_v1(token))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():

    token = request.args.get('token')
    channel_id = request.args.get('channel_id')

    return dumps(channel_details_v1(token, int(channel_id)))
    
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2(): 
    
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    return dumps(channel_messages_v1(token, int(channel_id), int(start)))

@APP.route('/channel/leave/v1', methods=['POST'])
def channel_leave_v2():

    request_data = request.get_json()

    return dumps(
        channel_leave_v1(
            request_data['token'],
            request_data['channel_id']
        )
    )

@APP.route("/message/send/v1", methods=['POST'])
def message_send_v1():

    input = request.get_json()

    return dumps(message_send(input['token'],
                              int(input['channel_id']),
                              input['message']))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_v1():

    input = request.get_json()

    return dumps(message_senddm(input['token'],
                                input['dm_id'],
                                input['message']))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1():

    input = request.get_json()

    return dumps(
        message_remove(
            input['token'],
            input['message_id']
        )
    )

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1():
    input = request.get_json()

    return dumps(
        message_edit(
            input['token'],
            input['message_id'],
            input['message']
        )
    )

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_v1():
    input = request.get_json()

    return dumps(message_pin(input['token'],
                             input['message_id']))

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin_v1():
    input = request.get_json()

    return dumps(message_unpin(input['token'],
                             input['message_id']))
                             
@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1():

    data = request.get_json()

    return dumps(
        message_react(
            data['token'],
            data['message_id'],
            data['react_id']
        )
    )


@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_v1():

    data = request.get_json()

    return dumps(
        message_unreact(
            data['token'],
            data['message_id'],
            data['react_id']
        )
    )

@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():

    data = request.get_json()

    return dumps(
        message_share(
            data['token'],
            data['og_message_id'],
            data['message'],
            data['channel_id'],
            data['dm_id']
        )
    )
    
@APP.route('/message/sendlater/v1', methods=['POST'])
def message_sendlater_v1():

    args = request.get_json()

    return dumps(message_sendlater(args['token'],
                                   args['channel_id'], 
                                   args['message'], 
                                   args['time_sent']))

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def message_sendlaterdm_v1():

    args = request.get_json()

    return dumps(message_sendlaterdm(args['token'],
                                   args['dm_id'], 
                                   args['message'], 
                                   args['time_sent']))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1():

    input = request.get_json()

    return dumps(dm_create(input['token'],
                           input['u_ids']))
    
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1():

    token = request.args.get('token')

    return dumps(dm_list(token))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_v1():

    input = request.get_json()

    return dumps(dm_remove(input['token'], input['dm_id']))
    
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1():

    token = request.args.get('token')
    dm_id = request.args.get('dm_id')

    return dumps(dm_details(token, int(dm_id)))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1():

    input = request.get_json()

    return dumps(dm_leave(input['token'], input['dm_id']))

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_v1():

    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')

    return dumps(dm_messages(token, int(dm_id), int(start)))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():

    # Get request_data from request
    request_data = request.get_json()

    return dumps(channel_join_v1(request_data['token'],
                                 request_data['channel_id']))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():

    # Get request_data from request
    request_data = request.get_json()

    return dumps(channel_invite_v1(request_data['token'],
                                   request_data['channel_id'],
                                   request_data['u_id']))

@APP.route('/channel/addowner/v1', methods=['POST'])
def channel_addowner_v2():

    input = request.get_json()

    return dumps (
        channel_addowner_v1(
            str(input['token']),
            int(input['channel_id']), 
            int(input['u_id']))
    )

@APP.route('/channel/removeowner/v1', methods=['POST'])
def channel_removeowner_v2():

    input = request.get_json()

    return dumps(channel_removeowner_v1(str(input['token']),
                                        int(input['channel_id']), 
                                        int(input['u_id'])))

@APP.route('/users/all/v1', methods=['GET'])
def users_all_v1():

    token = request.args.get("token")

    return dumps(users_all(token))

@APP.route('/user/profile/v1', methods=['GET'])
def user_profile_v1():

    token = request.args.get("token")
    u_id = request.args.get('u_id')

    return dumps(user_profile(token, int(u_id)))

@APP.route('/user/profile/setname/v1', methods=['PUT'])
def user_profile_setname_v1():
    
    input = request.get_json()

    return dumps (
        user_profile_setname(str(input['token']),
                            input['name_first'],
                             input['name_last'])
    )

@APP.route('/user/profile/setemail/v1', methods=['PUT'])
def user_profile_setemail_v1():

    input = request.get_json()

    return dumps(
        user_profile_setemail(input['token'], input['email'])
    )

@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def user_profile_sethandle_v1():

    input = request.get_json()

    return dumps(user_profile_sethandle(input['token'], 
                                        input['handle_str']))

@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def user_profile_uploadphoto_v1():

    data = request.get_json()

    return dumps(user_profile_uploadphoto(
                    data["token"],
                    data['img_url'],
                    data['x_start'],
                    data['y_start'],
                    data['x_end'],
                    data['y_end'],
    ))

@APP.route("/static/<path:path>")
def static_get_image(path):
    
    return send_from_directory('', path)

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_permission_change_v1():

    input = request.get_json()

    return dumps (
        admin_user_permission_change_v1(
            str(input['token']),
            int(input['u_id']),
            int(input['permission_id']))
    )
    
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_remove_user_v1():

    input = request.get_json()

    return dumps (
        admin_user_remove_v1(
            str(input['token']),
            int(input['u_id']))
    )
    
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_password_reset_request_v1():

    input = request.get_json()

    return dumps(auth_password_reset_request(input['email']))
                 
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_password_reset_v1():

    input = request.get_json()

    return dumps(auth_password_reset(input['reset_code'], 
                                     input['new_password']))
    
@APP.route('/user/stats/v1', methods=['GET'])
def user_stats_v1():

    token = request.args.get('token')

    return dumps(user_stats(token))

@APP.route('/notifications/get/v1', methods=['GET'])
def get_notifications_v1():

    token = request.args.get('token')

    return dumps(get_notifications(token))
@APP.route('/users/stats/v1', methods=['GET'])
def users_stats_v1():

    token = request.args.get('token')

    return dumps(users_stats(token))

@APP.route("/search/v1", methods=['GET'])
def search_v1():

    token = request.args.get("token")
    query_str = request.args.get('query_str')

    return dumps(search(token, query_str))

@APP.route("/standup/start/v1", methods=['POST'])
def start_standup_v1():

    input = request.get_json()

    return dumps (
        standup_start(
            str(input['token']),
            int(input['channel_id']),
            int(input['length']))
    )

@APP.route("/standup/active/v1", methods=['GET'])
def active_standup_v1():

    token = request.args.get("token")
    channel_id = request.args.get("channel_id")
    return dumps (
        standup_active(
            str(token),
            int(channel_id))
    )

@APP.route("/standup/send/v1", methods=['POST'])
def send_standup_v1():

    input = request.get_json()

    return dumps (
        standup_send(
            str(input['token']),
            int(input['channel_id']),
            str(input['message']))
    )

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    
    clear_v1()
    
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
