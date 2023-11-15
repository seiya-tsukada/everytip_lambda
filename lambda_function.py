import json
import base64
import os
import pprint
import requests
from urllib.parse import parse_qs
from datetime import datetime
import time

import boto3


token = os.environ["SLACK_OAUTH_TOKEN"]

# dynamodb = boto3.resource("dynamodb", region_name = "ap-northeast-1")
# table = dynamodb.Table("fpos_db")

dynamodb = boto3.client("dynamodb", region_name = "ap-northeast-1")
# DDB_TABLE_NAME = "fpos_db"
FPOS_TIPS_TABLE_NAME = "fpos_tips"
FPOS_USER_TABLE_NAME = "fpos_user_db"

def lambda_handler(event, context):
    
    #################
    # list of procedure
    # 1. get and parse event
    # 1.1. validation format from text in event
    # 2. get to and from user information (from fpos_user_db)
    # 2.1. judgement whether available user or not
    # 3. grant tip from user to to user
    # 3.1. insert transaction (to fpos_tips)
    # 4. update from user and to user (to fpos_user_db)
    # 5. send notification via slack and response
    #
    #
    #################

    # initialize
    res = ""
    body = ""
    res_dict = {}
    text_ret = ""

    user_id = ""
    user_name = ""



    # 1. get and parse event
    if event:
        body = base64.b64decode(event["body"]).decode("utf-8")
        res = parse_qs(body)
    else:
        return {
            'statusCode': 500,
            'body': "internal service error"
        }
       
    print("event")
    pprint.pprint(res)
   
    # parse event
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
   
    # print("res_dict")
    # pprint.pprint(res_dict)
  
    # 1.1. validation format from text in event
    text_ret = text_validation(res["text"][0]) # format is [to_user*] [amount*] [message*]
    if not isinstance(text_ret, dict): # Error if text_ret does not have a list
        return {
            'statusCode': 400,
            'body': text_ret
        }
    
    print("text ret")
    pprint.pprint(text_ret)



    #########################



    # 2. get to and from user information (from fpos_user_db)
    # get from user information
    from_user_info = ""
    from_user_info = get_user_info(res["user_name"][0])
    print("print: from_user_info")
    pprint.pprint(from_user_info)
    if not isinstance(from_user_info, dict): # Error if text_ret does not have a list
        return {
            'statusCode': 400,
            'body': "{} is not found".format(res["user_name"][0])
        }

    # get to user information
    to_user_info = ""
    to_user_info = get_user_info(text_ret["to_user_name"])
    print("print: to_user_info")
    pprint.pprint(to_user_info)
    if not isinstance(to_user_info, dict): # Error if text_ret does not have a list
        return {
            'statusCode': 400,
            'body': "{} is not found".format(res["user_name"][0])
        }

    # 2.1. judgement whether available user or not
    user_val_ret = ""
    user_val_ret = user_validation(from_user_info, to_user_info)

    print("user val ret")
    pprint.pprint(user_val_ret)
    if user_val_ret != "SUCCESS": # Error if user_val_ret is False
        return {
            'statusCode': 400,
            'body': user_val_ret
        }
    
    # 3. grant tip from user to to user
    grant_tip_ret = ""
    grant_tip_ret = grant_tip(from_user_info, to_user_info, text_ret["amount"])

    print("grant tip ret")
    pprint.pprint(grant_tip_ret)
    if grant_tip_ret != "SUCCESS": # Error if grant_tip_ret is False
        return {
            'statusCode': 400,
            'body': "grant operation is failed"
        }
    
    # 5. send notification via slack and response
    post_message_to_user = "{from_user} は {to_user} に {amount}everytip を送りました".format(from_user=from_user_info["user_name"]["S"], to_user=to_user_info["user_name"]["S"], amount=text_ret["amount"])
    print("post message 'to user'")
    print(post_message_to_user)

    data = {}
    data = {
        # "channel": conversations_open_res["channel"]["id"],
        "text": post_message_to_user,
    }

    # message via dm "to user"
    # post_message_via_dm(data)

    post_message_from_user = "残everytipは {} tip です".format(from_user_info["amount"]["N"])
    print("post message 'from user'")
    print(post_message_from_user)

    data = {}
    data = {
        # "channel": conversations_open_res["channel"]["id"],
        "text": post_message_from_user,
    }

    # message via dm "from user"
    # post_message_via_dm(data)


    return {
        'statusCode': 200,
        'body': post_message
    }
 

    # # # Open DM
    # dm_open_url = "https://slack.com/api/conversations.open?users={user_id}".format(user_id=res["user_id"][0])
    # print("dm open url")
    # pprint.pprint(dm_open_url)

    # headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }

    # # dm_open_res = requests.get(dm_open_url, headers=headers)
    # dm_open_res = requests.post(dm_open_url, headers=headers)
    # print("get DM channel")
    # pprint.pprint(dm_open_res.content)

   



  



def text_validation(text):

    ret = ""
    ts = text.split()
    message = ""
    
    # print(ts[0])
    # print(ts[1])
    # print(ts[2])

    if len(ts) != 3:
        message = "invalid parameter"
        return message
       
    if not ts[1].isnumeric():
        message = "invalid format of amount information"
        return message
    
    ret = {
        # remove @ (mention prefix)
        "to_user_name": ts[0].removeprefix("@"),
        "amount": ts[1],
        "message": ts[2]
    }
    
    return ret

def get_user_info(user_name):

    print("get " + user_name +  " info section")

    res = ""

    option = {
        "TableName": FPOS_USER_TABLE_NAME,
        "IndexName": "GSI-user_name",
        "KeyConditionExpression": "user_name = :user_name",
        "ExpressionAttributeValues": {
        ":user_name": {
            "S": user_name}

        }
    }
    res = dynamodb.query(**option)
    
    if res["Count"] > 0:
        return res["Items"][0]
    else:
        return None

def user_validation(from_user, to_user):

    print("in user validation function")
    print("from_user")
    pprint.pprint(from_user)
    print("to_user")
    pprint.pprint(from_user)

    # Fail if from user and to user are the same person.
    if from_user["user_id"]["S"] == to_user["user_id"]["S"]:
        message = "from user and to user are same person"
        return message

    # is available? from_user
    if not from_user["is_available"]["BOOL"]:
        message = "{} is not available".format(from_user["user_name"]["S"])
        return message

    # is available? to_user
    if not to_user["is_available"]["BOOL"]:
        message = "{} is not available".format(to_user["user_name"]["S"])
        return message
    
    return "SUCCESS"

def grant_tip(from_user, to_user, amount):

    print("grant tip ret function")

    if int(from_user["wallet"]["N"]) - int(amount) < 0:
        message = "{} is not enough tip".format(from_user["user_name"]["S"])
        return message
    
    # 3.1. insert transaction (to fpos_tips)
    # insert transaction information
    insert_transaction_information(from_user, to_user, amount)

    # 4. update from user and to user (to fpos_user_db)
    # grant money
    update_user_information(from_user, int(from_user["wallet"]["N"]) - int(amount))
    
    # subtract money
    update_user_information(to_user, int(to_user["wallet"]["N"]) + int(amount))

    return "SUCCESS"

def update_user_information(user, amount):

    print("update " + user["user_name"]["S"] + " information")

    res = ""
    option = ""

    option = {
        "TableName": FPOS_USER_TABLE_NAME,
        "Key": {
           "user_id": {"S": user["user_id"]["S"]}
        },
        "UpdateExpression": "set wallet = :wallet",
        'ExpressionAttributeValues': {
            ":wallet": {"N": str(amount)},
        }
    }

    pprint.pprint(option)
    res = dynamodb.update_item(**option)
 
    return res["ResponseMetadata"]["HTTPStatusCode"]

def insert_transaction_information(from_user, to_user, amount):

    print("insert {0} {1} information".format(from_user["user_name"]["S"], to_user["user_name"]["S"]))
 
    data = ""
    option = ""

    data = {
        "id": {"S": "et_"+str(int(time.time() * 1000))},
        "from_user_id": {"S": from_user["user_id"]["S"]},
        "from_user_name": {"S": from_user["user_name"]["S"]},
        "to_user_id": {"S": to_user["user_id"]["S"]},
        "to_user_name": {"S": to_user["user_name"]["S"]},
        "amount": {"N": amount},
        "created_at": {"S": datetime.now().isoformat(timespec="seconds")},
    }

    pprint.pprint(data)

    option = {
        "TableName": FPOS_TIPS_TABLE_NAME,
        "Item": data,
    }

    dynamodb.put_item(**option)

    return "SUCCESS"

def post_message_via_dm(data):

    ret = ""
    chat_url = "https://slack.com/api/chat.postMessage"

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    ret = requests.post(chat_url, headers=headers, data=json.dumps(data))

    print("POST OK")
    pprint.pprint(ret)

    return ret

# def dynamo_get(user_id):
    
#     print("dynamo_get_part 1")

#     res = ""

#     option = {
#         "TableName": DDB_TABLE_NAME,
#         "Key": {
#             "user_id": {"S": user_id}
#         }
#     }
#     res = dynamodb.get_item(**option)
    
#     pprint.pprint(res)
#     pprint.pprint(res["Item"])

#     return

# def dynamo_update(user_id):

#     res = ""    
#     option = ""

#     option = {
#          "TableName": DDB_TABLE_NAME,
#          "Key": {
#             "user_id": {"S": user_id}
#         },
#         "UpdateExpression": "set attr1 = :attr1, attr2 = :attr2",
#         'ExpressionAttributeValues': {
#             ":attr1": {"S": "test"},
#             ":attr2": {"S": "abcde"},
#         }
#     }
    
#     res = dynamodb.update_item(**option)
#     pprint.pprint(res)
 
#     return


