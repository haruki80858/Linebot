import os
import pya3rt
from flask import Flask, request, abort

from linebot import(
        LineBotApi, WebhookHandler
)
from linebot.exceptions import(
        InvalidSignatureError
)
from linebot.models import(
        MessageEvent, TextMessage, TextSendMessage,
)

app=Flask(__name__)

line_bot_api = LineBotApi('ztUdrom/e+1GsKH69mZO+/H22WmqciYpL/YwouQ+6mCT9/OYE3DKnLW8wkDm2nD3Nws/u7fGj6QhQfDztyHxmSByj7kJDbG1RpAl0X/x6ASqD2sfxE581GUQacR7PnGiAS+F8//NK+/3xjKUfeKnRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('49e8fd1fecf12f92390cf3c0adabaeab')

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
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply=create_reply(event.message.text)
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
def create_reply(user_text):
    apikey="DZZK8lrwFyRhL8rOtGlmhCizKN2we20G"
    client=pya3rt.TalkClient(apikey)
    res=client.talk(user_text)

    return res['results'][0]['reply']

if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host='0.0.0.0',port=port)
    app.run()
