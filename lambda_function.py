import json
import base64
import os
import pprint
import requests
from urllib.parse import parse_qs
import boto3



token = os.environ["SLACK_OAUTH_TOKEN"]

dynamodb = boto3.resource("dynamodb", region_name = "ap-northeast-1")
table = dynamodb.Table("fpos_db")

def lambda_handler(event, context):
    # TODO implement
   
    res = ""
    body = ""
    res_dict = ""

    # dynamoDB
    print("dynamo part")
    dynamo_operate()




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
    pprint.pprint(res["text"])
   

    # # Open DM
    dm_open_url = "https://slack.com/api/conversations.open?users={user_id}".format(user_id=res["user_id"][0])
    print("dm open url")
    pprint.pprint(dm_open_url)

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }

    dm_open_res = requests.get(dm_open_url, headers=headers)
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

def dynamo_operate():

    data = {
        "user_id": "ghi",
        "attr1": "attr111",
        "attr2": "attr222"
    }
    
    dynamo_insert(data)
    dynamo_search("ghi")
    # update(event)
    # delete(event)

    return

def dynamo_insert(data):
    
    table.put_item(
        Item=data
    )
    return

def dynamo_search(data):
    
    res = ""

    res = table.get_item(
        Key={
            "user_id": data
        }
    )

    print("dynamo_search_part")
    pprint.pprint(res["Item"])

    return


def post_message_to_the_channel(data):

    ret = ""
    chat_url = "https://slack.com/api/chat.postMessage"

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    ret = requests.post(chat_url, headers=headers, data=json.dumps(data))

    print("POST OK")

    return ret