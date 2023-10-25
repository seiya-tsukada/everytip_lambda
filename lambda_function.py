import json
import base64
import os
import pprint
import requests
from urllib.parse import parse_qs
import boto3



token = os.environ["SLACK_OAUTH_TOKEN"]

# dynamodb = boto3.resource("dynamodb", region_name = "ap-northeast-1")
# table = dynamodb.Table("fpos_db")

dynamodb = boto3.client("dynamodb", region_name = "ap-northeast-1")
DDB_TABLE_NAME = "fpos_db"

def lambda_handler(event, context):
    # TODO implement
   
    res = ""
    body = ""
    res_dict = ""
    text_ret = ""




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
    pprint.pprint(text_ret)

    #########################


    # dynamoDB
    print("dynamo insert part")
    # dynamo_operate(res["user_id"][0], res["user_name"][0], text_ret["amount"])

    
    dynamo_insert(res["user_id"][0], res["user_name"][0], text_ret["amount"])


    # # Open DM
    dm_open_url = "https://slack.com/api/conversations.open?users={user_id}".format(user_id=res["user_id"][0])
    print("dm open url")
    pprint.pprint(dm_open_url)

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }

    # dm_open_res = requests.get(dm_open_url, headers=headers)
    dm_open_res = requests.post(dm_open_url, headers=headers)
    print("get DM channel")
    pprint.pprint(dm_open_res.content)

   




    data = {
        "channel": "fpos",
        "text": res["text"][0],
    }

    # message to the channel
    post_message_to_the_channel = data
  

    return {
        'statusCode': 200,
        'body': res["text"][0]
    }

def text_validation(text):

    ret = ""
    ts = text.split()
    
    print(ts[0])
    print(ts[1])
    print('isnumeric:', ts[1].isnumeric())
    print(ts[2])

    ret = {
        "to_mention_name": ts[0],
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

    data = {
        "user_id": user_id,
        "user_name": user_name,
        "wallet": amount,
        "attr1": "attr1111",
        "attr2": "attr2222"
    }

    print("dynamo insert part in")
    print("data")
    print(data)
    print(type(data))
    print({"----end----"})

    option = {
        "TableName": DDB_TABLE_NAME,
        # "Item": data
        "Item": {
            "user_id": "user_id",
            "user_name": "user_name",
            "wallet": "amount",
            "attr1": "attr1111",
            "attr2": "attr2222"
        }
    }

    dynamodb.put_item(**option)

    return

def dynamo_get(user_id):
    
    res = ""

    option = {
        "TableName": DDB_TABLE_NAME,
        "Key": {
            "user_id": user_id
        }
    }
    res = dynamodb.put_item(option)
    print("dynamo_get_part")
    pprint.pprint(res)
    pprint.pprint(res["Item"])

    return

def dynamo_update(data):

    res = ""    
    option = ""

    option = {
         "TableName": DDB_TABLE_NAME,
         "Key": {
            "user_id": user_id
        },
        "UpdateExpression": 'set attr1 = :attr1',
        'ExpressionAttributeValues': {
            ":attr1": "test"
        }
    }
    
    res = dynamodb.update_item(data)
    pprint.pprint(res["Attributes"])
 
    return


def post_message_to_the_channel(data):

    ret = ""
    chat_url = "https://slack.com/api/chat.postMessage"

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    ret = requests.post(chat_url, headers=headers, data=json.dumps(data))

    print("POST OK")

    return ret