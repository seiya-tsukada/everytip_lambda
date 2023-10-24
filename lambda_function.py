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
    text_ret = text_validation(res["text"])
    pprint.pprint(text_ret)

    #########################


    # dynamoDB
    print("dynamo part")
    dynamo_operate(res["user_id"][0], )



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

def text_validation(text):

    ret = ""
 
    print(text[0])
    print(text[1])
    print('isnumeric:', text[1].isnumeric())
    print(text[2])

    ret = {
        "mention_name": text[0],
        "amount": text[1],
        "message": text[2]
    }
    
    return ret

def dynamo_operate(user_id):

    data = {
        "user_id": user_id,
        "attr1": "attr1111",
        "attr2": "attr2222"
    }
    
    dynamo_insert(data)
    dynamo_search(user_id)
    # update(event)
    # delete(event)

    return

def dynamo_insert(user_id):
    
    table.put_item(
        Item=user_id
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