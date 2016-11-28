# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import errno
import logging
import os
import re
import time

import redis

from flask_sqlalchemy import SQLAlchemy

from flask import Flask, request, abort, send_from_directory

from linebot import (
    LineBotApi, WebhookHandler,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    ImagemapSendMessage, MessageImagemapAction, MessageImagemapAction, BaseSize, ImagemapArea
)

from lock import Lock


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
redis = redis.from_url(app.config['REDIS_URL'])
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

from app.models import Poker

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])

mapping = {"0":"0", "1":"1", "2":"2", "3":"3", "4":"5", "5":"8", "6":"13", "7":"20", "8":"40", "9":"?", "10":"∞", "11":"Soy"}

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@app.route('/images/planning_poker/<size>', methods=['GET'])
def images(size):
    app.logger.info(size)
    return send_from_directory("static/planning_poker/", "pp-" + size +".png")


def getSourceId(source):
    sourceType = source.type
    if sourceType == 'user':
        app.logger.info("user id : " + source.user_id)
        return source.user_id
    elif sourceType == 'group':
        app.logger.info("group id : " + source.group_id)
        return source.group_id
    elif sourceType == 'room':
        app.logger.info("room id : " + source.room_id)
        return source.room_id
    else:
        abort(400)

MUTEX_KEY = 'MUTEX'
VOTE_PATTERN = r"^#(\d+) (.+)"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    sourceId = getSourceId(event.source)
    matcher = re.match(VOTE_PATTERN, text)

    if text == 'プラポ':
        lock = Lock(redis, MUTEX_KEY + '_POKER_' + sourceId)
        lock.lock()
        if lock.is_lock():
           poker = Poker(redis, sourceId)
           line_bot_api.reply_message(
               event.reply_token,
               poker.generatePlanningPokerMessage())
           time.sleep(20)
           lock.unlock()
    elif matcher is not None:
        count = matcher.group(1)
        location = matcher.group(2)
        vote_key = sourceId + count
        mutex = Lock(redis, MUTEX_KEY + '_VOTE_' + sourceId)
        mutex.lock()
        if mutex.is_lock():
            time.sleep(10)
            redis.hincrby(vote_key, location)
            message =  'ポーカーの結果\n'
            for i in range(0, 12):
                result = redis.hget(vote_key, str(i))
                if result is None:
                    result = 0
                message += mapping[str(i)] + 'は' + str(result) + '人\n'
            confirm_message = ConfirmTemplate(
                text=message,
                actions=[
                    MessageTemplateAction(label='もう１回', text='プラポ'),
                    MessageTemplateAction(label='やめる', text='やめる'),
                ]
            )
            template_message = TemplateSendMessage(
                alt_text='結果', template=confirm_message)
            line_bot_api.reply_message(
                event.reply_token,
                template_message
            )
            mutex.unlock()
        else:
            redis.hincrby(vote_key, location)

