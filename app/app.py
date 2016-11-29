#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import errno
import logging
import os
import re
import redis
import time

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
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    ImagemapSendMessage, MessageImagemapAction, BaseSize, ImagemapArea
)

import const

from line_util import *
from mutex import Mutex

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
redis = redis.from_url(app.config['REDIS_URL'])
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(app.config['LOG_LEVEL'])

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
    filename = const.POKER_IMAGE_FILENAME.replace('{$0}', size)
    return send_from_directory("static/planning_poker/", filename)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    sourceId = getSourceId(event.source)
    matcher = re.match(r"^#(\d+) (.+)", text)

    if text == 'プラポ':
        mutex = Mutex(redis, const.POKER_MUTEX_KEY_PREFIX+ sourceId)
        mutex.lock()
        if mutex.is_lock():
           number = str(redis.incr(sourceId)).encode('utf-8')
           line_bot_api.reply_message(
               event.reply_token,
               generate_planning_poker_message(number))
           time.sleep(const.POKER_MUTEX_TIMEOUT)
           mutex.unlock()
    elif matcher is not None:
        count = matcher.group(1)
        location = matcher.group(2)
        vote_key = sourceId + count
        mutex = Mutex(redis, const.VOTE_MUTEX_KEY_PREFIX  + sourceId)
        mutex.lock()
        if mutex.is_lock():
            time.sleep(const.VOTE_MUTEX_TIMEOUT)
            redis.hincrby(vote_key, location)
            line_bot_api.reply_message(
                event.reply_token,
                genenate_voting_result_message(vote_key)
            )
            mutex.unlock()
        else:
            redis.hincrby(vote_key, location)

def genenate_voting_result_message(key):
    message =  'ポーカーの結果\n'
    for i in range(0, 12):
        result = redis.hget(key, str(i))
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
    return template_message

def generate_planning_poker_message(number):
    message = ImagemapSendMessage(
        base_url='https://scrummasterbot.herokuapp.com/images/planning_poker',
        alt_text='this is planning poker',
        base_size=BaseSize(height=790, width=1040))
    actions=[]
    location=0
    for i in range(0, 3):
        for j in range(0, 4):
            actions.append(MessageImagemapAction(
                text = u'#' + number + u' ' + str(location).encode('utf-8'),
                area=ImagemapArea(
                    x=j * const.POKER_IMAGEMAP_ELEMENT_WIDTH,
                    y=i * const.POKER_IMAGEMAP_ELEMENT_HEIGHT,
                    width=(j + 1) * const.POKER_IMAGEMAP_ELEMENT_WIDTH,
                    height=(i + 1) * const.POKER_IMAGEMAP_ELEMENT_HEIGHT
                )
            ))
            location+=1
    message.actions = actions
    return message
