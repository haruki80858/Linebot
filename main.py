from base64 import b64encode
from sys import argv
import json
import requests
import numpy as np
from pathlib import Path
import sys
import os
import pya3rt
from googletrans import Translator
from flask import Flask, request, abort
from linebot import(
        LineBotApi, WebhookHandler
)
from linebot.exceptions import(
        InvalidSignatureError
)
from linebot.models import(
        MessageEvent, TextMessage,ImageMessage, TextSendMessage,
)

app=Flask(__name__)
translator = Translator()
line_bot_api = LineBotApi(os.environ['LINEBOTAPI'])
handler = WebhookHandler(os.environ['WEBHOOKHANDLER'])


@app.route("/callback",methods=['POST'])
def callback():
    signature=request.headers['X-Line-Signature']

    body=request.get_data(as_text=True)
    app.logger.info("Request body: "+body)

    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        print("Invalid signature.Please check your channel access token/channel secret")
        abort(400)
    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    print("[INFO] received text")
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply=create_reply(event.message.text)
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    with open(Path(f"images/gazo.jpg").absolute(), "wb") as f:
        print("[INFO] image is opening")
        for chunk in message_content.iter_content():
            f.write(chunk)

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=vgg('images/gazo.jpg')))
    
def create_reply(user_text):
    client=pya3rt.TalkClient(os.environ['REPLY_APIKEY'])
    res=client.talk(user_text)

    return res['results'][0]['reply']

def vgg(i):

    ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
    img_requests = []
    with open(i, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 5
                    }]
            })

    response = requests.post(ENDPOINT_URL,
                             data=json.dumps({"requests": img_requests}).encode(),
                             params={'key':os.environ['CLOUD_VISION_API']},
                             headers={'Content-Type': 'application/json'})
    txt=translator.translate(response.json()['responses'][0]['labelAnnotations'][0]['description'], dest='ja')
    return txt.text




if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host='0.0.0.0',port=port)
    
