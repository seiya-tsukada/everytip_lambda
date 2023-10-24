import json
import base64
# import requests
import urllib.request
from urllib.parse import parse_qs

def lambda_handler(event, context):
    # TODO implement
   
    res = ""
    body = ""
    res_dict = ""
    text = ""
   
    url = "https://slack.com/api/chat.postMessage"
    token = "xoxb-5099821813942-6069344184835-M9GyCFytlJt9CdXrrxglYzpM"
   
    if event:
        body = base64.b64decode(event["body"]).decode("utf-8")
        res = parse_qs(body)
    else:
        res = "hello fpos"
   
    text = res["text"]
    print(res)
    print(res["user_id"])
    print(res["user_name"])
    print(res["channel_id"])
    print("text: " + text[0])
   
    res_dict = {
        "user_id": res["user_id"],
        "user_name": res["user_name"],
        "channel_id": res["channel_id"]
        #"text": res["text"]
    }
   
    print(type(text))
    print(res_dict)
   


    data = {
        "channel" : "fpos",
        "text" : text[0]
       
    }

    method = 'POST'
    # request_headers = { 'Content-Type': 'application/json; charset=utf-8' }
    headers = { "Authorization": "Bearer {}".format(token), 'Content-Type': 'application/json; charset=utf-8' }
    body = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=body,
        method=method,
        headers=headers
    )
    with urllib.request.urlopen(request) as res:
        ans = res.read()
   
    print(ans)
   
   
   
    return {
        'statusCode': 200,
        'body': res_dict
    }