import json
import base64
import os
import pprint
import requests
from urllib.parse import parse_qs
import boto3



token = os.environ["SLACK_OAUTH_TOKEN"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("fpos_db")

def lambda_handler(event, context):
    # TODO implement
   
    res = ""
    body = ""
    res_dict = ""
    
   
    
    # token = os.environ["SLACK_OAUTH_TOKEN"]
   



    # dynamoDB
    dynamo_operate()









    # pprint.pprint(token)

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
   
    print("res_dict and res_text")
    pprint.pprint(res_dict)
    pprint.pprint(res["text"])
   

    # # Open DM
    # dm_open_url = "https://slack.com/api/conversations.open?users={user_id}".format(user_id=res["user_id"][0])
    # pprint.pprint(dm_open_url)
    # method = "GET"
    # headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    # # body = json.dumps(data).encode("utf-8")
    # request = urllib.request.Request(
    #     url=dm_open_url,
    #     # data=body,
    #     method=method,
    #     headers=headers
    # )
    # with urllib.request.urlopen(request) as res:
    #     ans = res.read()    
    #     ans = ans.json()
    #     print("GET OK")
    #     pprint.pprint(ans)

    # print("get DM channel")




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
        "user_id": "abc",
        "attr1": "attr1",
        "attr2": "attr2"
    }
    # search(event)
    dynamo_insert(data)
    # update(event)
    # delete(event)

    return

def dynamo_insert(data):
    
    table.put_item(
        Item=data
    )
    return



def post_message_to_the_channel(data):

    ret = ""
    chat_url = "https://slack.com/api/chat.postMessage"

    headers = { "Authorization": "Bearer {}".format(token), "Content-Type": "application/json; charset=utf-8" }
    ret = requests.post(chat_url, headers=headers, data=json.dumps(data))

    print("POST OK")

    return ret