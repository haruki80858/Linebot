import numpy as np
from pathlib import Path
import sys
import os
import pya3rt
from googletrans import Translator
from PIL import Image
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image
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
line_bot_api = LineBotApi('KGDQXjG0Ejq/78oKURA5vBitMuWeUWSZFixddvR/pk6CdUKJL5icOT6RWNnD30q+Nws/u7fGj6QhQfDztyHxmSByj7kJDbG1RpAl0X/x6AQvdGtAoEaHd32OB5anOVNYENOYa+Rp2JDpbn6Lr0jD+wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('576dc6cd6186cfbfd9f97baebb40cf44')

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

@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    with open(Path(f"images/gazo_1.jpg").absolute(), "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=vgg('images/gazo.jpg')))
    
def create_reply(user_text):
    apikey="DZZK8lrwFyRhL8rOtGlmhCizKN2we20G"
    client=pya3rt.TalkClient(apikey)
    res=client.talk(user_text)

    return res['results'][0]['reply']

def vgg(i):
    filename = i
    # モデルの設定
    model = VGG16(weights='imagenet')
    # 入力するデータを読み込み整形
    img = image.load_img(filename, target_size=(224, 224))
    # 画像を配列に変換
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    # モデルにかけて推論
    preds = model.predict(preprocess_input(x))
    results = decode_predictions(preds, top=5)[0]
    # 推論結果を出
    txt=translator.translate(results[0][1], dest='ja')
    return txt.text


if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host='0.0.0.0',port=port)
    
