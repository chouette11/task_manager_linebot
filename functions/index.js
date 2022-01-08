'use strict';

const functions = require('firebase-functions');
const express = require('express');
const line = require('@line/bot-sdk');
const admin = require('firebase-admin');
const { firestore } = require('firebase-admin');
admin.initializeApp(functions.config().firebase);
const db = admin.firestore();

const config = {
    channelSecret: '',
    channelAccessToken: ''
};

const app = express();

app.post('/webhook', line.middleware(config), (req, res) => {
    Promise
      .all(req.body.events.map(handleEvent))
      .then((result) => res.json(result));
});

const client = new line.Client(config);

async function handleEvent(event) {
  if (event.type === 'message') {
    
    return client.replyMessage(
        event.replyToken,
        {
          "type": "template",
          "altText": "this is a confirm template",
          "template": {
              "type": "confirm",
              "text": `${event.message.text}`,
              "actions": [
                  {
                    "type":"datetimepicker",
                    "label":"締切を選択",
                    "data":`${event.message.text}`,
                    "mode":"datetime",
                    "min":"2018-01-24t23:59",
                    "max":"2040-12-25t00:00"
                  },
                  {
                    "type": "message",
                    "label": "キャンセル",
                    "text": "no"
                  }
              ]
          }
        }
    )
  }

  if (event.type !== 'message') {

    const userRef = db.collection("tasks").doc("フクダ");

    const limit = new Date(event.postback.params['datetime'])

    limit.setHours(limit.getHours() - 9);

    await userRef
      .update({
        taskData: firestore.FieldValue.arrayUnion(
          {
            id: 100,
            limit: firestore.Timestamp.fromDate(limit),
            task: event.postback.data,
          }
        )
      });

    return client.pushMessage(
      event.source.userId,
      {
          type: 'text',
          text: `${event.postback.params['datetime']}`,
      },
    )
  }
}

exports.app = functions.https.onRequest(app);