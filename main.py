from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, PostbackEvent, TextMessage,TextSendMessage,DatetimePickerTemplateAction, TemplateSendMessage, ConfirmTemplate, MessageAction
import os

app=Flask(__name__)
#環境変数の取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api=LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler=WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback",methods=["POST"])
def callback():
    signature=request.headers["X-Line-Signature"]

    body=request.get_data(as_text=True)
    app.logger.info("Request body"+body)

    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(PostbackEvent)
def on_postback(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    postback_msg = event.postback

    line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text=postback_msg)
    )
    if postback_msg == 'is_show=1':
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='is_showオプションは1だよ！')
        )
    elif postback_msg == 'is_show=0':
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='is_showオプションは0だよ！')
        )

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='でいいですか？',
                    actions=[
                        DatetimePickerTemplateAction(
                            label='Setting',
                            data='action=settime',
                            mode='datetime',
                            min='2017-12-25t00:00',
                            max='2044-01-24t23:59'
                        ),
                        MessageAction(
                            label='だめ',
                            text='だめ'
                        )
                    ]
                )
            )
        )

if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0",port=port)
