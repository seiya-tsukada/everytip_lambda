import json
import base64
import os
import pprint
import requests
import sys
from urllib.parse import parse_qs

import boto3


token = os.environ["SLACK_OAUTH_TOKEN"]

# dynamodb = boto3.resource("dynamodb", region_name = "ap-northeast-1")
# table = dynamodb.Table("fpos_db")

dynamodb = boto3.client("dynamodb", region_name = "ap-northeast-1")
DDB_TABLE_NAME = "fpos_db"
FPOS_USER_TABLE_NAME = "fpos_user_db"

def lambda_handler(event, context):
    
    #################
    # list of procedure
    # 1. parse event
    # 2. get to from user information 
    
    
    
    
    
    # TODO implement
   
    res = ""
    body = ""
    res_dict = ""
    text_ret = ""

    user_id = ""
    user_name = ""


    # get event

    if event:
        body = base64.b64decode(event["body"]).decode("utf-8")
        res = parse_qs(body)
    else:
        res = "hello everytip"
       
    # print("res")
    # pprint.pprint(res)
   
    res_dict = {
        "api_app_id": res["api_app_id"][0],
        "channel_id": res["channel_id"][0],
        "channel_name": res["channel_name"][0],
        "command": res["command"][0],
        "response_url": res["response_url"][0],
        "team_domain": res["team_domain"][0],
        "token": res["token"][0],
        "trigger_id": res["trigger_id"][0],
        "user_id": res["user_id"][0],
        "user_name": res["user_name"][0],
    }
   
    print("res_dict")
    pprint.pprint(res_dict)

    print("res_text")
    text_ret = text_validation(res["text"][0])
    if not isinstance(text_ret, list): # 値がリストがリストを返却しない場合、エラー
        return {
            'statusCode': 200,
            'body': text_ret
        }


    pprint.pprint(text_ret)

    #########################


    from_user_id = ""
    from_user_id = res["user_id"][0]
    from_user_name = ""
    from_user_name = res["user_name"][0]
    to_user_name = ""
    to_user_name = to_user=text_ret["to_user_name"]
                                    
    user_info = ""


    # dynamoDB
    print("dynamo get part")
    user_info = get_user_info(from_user_name, to_user_name)

    pprint.pprint(user_info)


    # test
    return


    print("dynamo insert part")
    # dynamo_operate(res["user_id"][0], res["user_name"][0], text_ret["amount"])

    
    dynamo_insert(res["user_id"][0], res["user_name"][0], text_ret["amount"])
    dynamo_get(res["user_id"][0])
    dynamo_update(res["user_id"][0])



    # # Open DM
    dm_open_url = "https://slack.com/api/conversations.open?users={user_id}".format(user_id=res["user_id"][0])
    print("dm open url")
    pprint.pprint(dm_open_url)

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }

    # dm_open_res = requests.get(dm_open_url, headers=headers)
    dm_open_res = requests.post(dm_open_url, headers=headers)
    print("get DM channel")
    pprint.pprint(dm_open_res.content)

   


    post_message = "{from_user} は {to_user} に {amount}everytip を送りました".format(to_user=text_ret["to_user_name"], from_user=res["user_name"][0], amount=text_ret["amount"])

    data = {
        "channel": "fpos",
        "text": post_message,
    }

    # message to the channel
    post_message_to_the_channel = data
  

    return {
        'statusCode': 200,
        'body': post_message
    }

def text_validation(text):

    ret = ""
    ts = text.split()
    message = ""
    
    # print(ts[0])
    # print(ts[1])
    # print(ts[2])

    print(len(ts))

    if len(ts) != 3:
        message = "invalid parameter"
        return message
       
    if not ts[1].isnumeric():
        message = "invalid format of amount information"
        return message
        
    ret = {
        "to_user_name": ts[0],
        "amount": ts[1],
        "message": ts[2]
    }
    
    return ret

def dynamo_operate(user_id, user_name, amount):

    # print("dynamo part in")
    # print("user_id")
    # print(user_id)
    # print(type(user_id))
    # print({"----end----"})

    data = {
        "user_id": user_id,
        "user_name": user_name,
        "wallet": amount,
        "attr1": "attr1111",
        "attr2": "attr2222"
    }
    
    dynamo_insert(data)
    dynamo_get(user_id)
    dynamo_update(user_id)
    # delete(event)

    return

def dynamo_insert(user_id, user_name, amount):
    
    data = ""
    option = ""

    data = {
        "user_id": {"S": user_id},
        "user_name": {"S": user_name},
        "wallet": {"N": amount},
        "attr1": {"S": "attr1111"},
        "attr2": {"S": "attr2222"},
    }

    option = {
        "TableName": DDB_TABLE_NAME,
        "Item": data,
    }

    dynamodb.put_item(**option)

    return


def get_user_info(from_user_name, to_user_name):

    print("get user info section")

    # list user
    user_list_url = "https://slack.com/api/users.list" 
    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }

    # dm_open_res = requests.get(dm_open_url, headers=headers)
    res = requests.get(user_list_url, headers=headers)
    # print("get DM channel")
    user_list_info = json.dumps(res.json(), indent=5)
    pprint.pprint(user_list_info)

    # res = ""

    # option = {
    #     "TableName": DDB_TABLE_NAME,
    #     "Key": {
    #         "user_id": {"S": user_id}
    #     }
    # }
    # res = dynamodb.get_item(**option)
    
    # pprint.pprint(res)
    # pprint.pprint(res["Item"])

    return




def dynamo_get(user_id):
    
    print("dynamo_get_part 1")

    res = ""

    option = {
        "TableName": DDB_TABLE_NAME,
        "Key": {
            "user_id": {"S": user_id}
        }
    }
    res = dynamodb.get_item(**option)
    
    pprint.pprint(res)
    pprint.pprint(res["Item"])

    return

def dynamo_update(user_id):

    res = ""    
    option = ""

    option = {
         "TableName": DDB_TABLE_NAME,
         "Key": {
            "user_id": {"S": user_id}
        },
        "UpdateExpression": "set attr1 = :attr1, attr2 = :attr2",
        'ExpressionAttributeValues': {
            ":attr1": {"S": "test"},
            ":attr2": {"S": "abcde"},
        }
    }
    
    res = dynamodb.update_item(**option)
    pprint.pprint(res)
 
    return


def post_message_to_the_channel(data):

    ret = ""
    chat_url = "https://slack.com/api/chat.postMessage"

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    ret = requests.post(chat_url, headers=headers, data=json.dumps(data))

    print("POST OK")

    return ret