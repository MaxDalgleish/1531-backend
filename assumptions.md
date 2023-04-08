# GENERAL ASSUMPTIONS
- **Assume all inputs will be of valid data type.**
- If a function requires subsequent functions to implement, then we assume the subsequent functions work.

## auth_login_v1
- Assume that email from registering will always be valid, therefore double 
checking for invalid email is not necessary.

## auth_register_v1
- Assume first and last name may contain non-alphanumerics.
- **Assume that if handle contains no alphanumeric chars, inputerror should be raised.**
- **Assume password does not have a length limit.**

## channels_create_v1
- Assume that channel name can consist of any characters.
- **There may be more than two channels with the same name, but with different channel id's.**

## channel_list_v1 
- N/A

## channels_listall_v1
- N/A

## channel_details_v1
- N/A

## channel_join_v1
- Assume that there is no limit on how many people can join the channel.

## channel_invite_v1
- **Assume that there is no limit on how many people can be invited to the channel.**

## channel_messages_v1
- **Assume that each message consists of a dictionary which contains message details such as time and message id.**

## clear_v1
- N/A