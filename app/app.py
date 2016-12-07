#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import errno
import logging
import os
import re
import redis
import time

from flask import Flask, request, abort, send_from_directory, url_for

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

from const import *
from utility import *
from mutex import Mutex

app = Flask(__name__)
app.config.from_object('config')
redis = redis.from_url(app.config['REDIS_URL'])
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(app.config['LOG_LEVEL'])
line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])
mapping = {"0":"0", "1":"1", "2":"2", "3":"3", "4":"5", "5":"8", "6":"13", "7":"20", "8":"40", "9":"?", "10":"∞", "11":"Soy"}

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route('/images/tmp/<number>/<filename>', methods=['GET'])
def download_result(number, filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'tmp', number), filename)

@app.route('/images/planning_poker/<size>', methods=['GET'])
def download_imagemap(size):
    filename = POKER_IMAGE_FILENAME.format(size)
    return send_from_directory(os.path.join(app.root_path, 'static', 'planning_poker'),
            filename)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    #from models import PlanningPokerResult
    text = event.message.text
    sourceId = getSourceId(event.source)
    matcher = re.match(r'^#(\d+) (.+)', text)

    if text == 'プラポ':
        mutex = Mutex(redis, POKER_MUTEX_KEY_PREFIX+ sourceId)
        mutex.lock()
        if mutex.is_lock():
           number = str(redis.incr(sourceId)).encode('utf-8')
           line_bot_api.reply_message(
               event.reply_token,
               generate_planning_poker_message(number))
           time.sleep(POKER_MUTEX_TIMEOUT)
           mutex.unlock()
    elif matcher is not None:
        number = matcher.group(1)
        location = matcher.group(2)
        current = redis.get(sourceId).encode('utf-8')
        if number != current:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text=MESSAGE_INVALID_VOTE.format(number)))
            return
        vote_key = sourceId + number 
        status = redis.hget(vote_key, 'status')
        if status is None:
            mutex = Mutex(redis, VOTE_MUTEX_KEY_PREFIX  + sourceId)
            mutex.lock()
            if mutex.is_lock():
                time.sleep(VOTE_MUTEX_TIMEOUT)
                redis.hincrby(vote_key, location)
                line_bot_api.reply_message(
                    event.reply_token,
                    genenate_voting_result_message(vote_key)
                )
                redis.hset(vote_key, 'status', 'complete')
                mutex.unlock()
            else:
                redis.hincrby(vote_key, location)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text=MESSAGE_END_POKER.format(number)))


def genenate_voting_result_message(key):
    data = redis.hgetall(key)
    tmp = generate_voting_result_image(data)
    buttons_template = ButtonsTemplate(
        title='ポーカー結果',
        text='そろいましたか？',
        thumbnail_image_url='https://scrummasterbot.herokuapp.com/images/tmp/' + tmp + '/result_11.png',
        actions=[
            MessageTemplateAction(label='もう１回', text='プラポ')
    ])
    template_message = TemplateSendMessage(
        alt_text='結果', template=buttons_template)
    return template_message

def generate_planning_poker_message(number):
    message = ImagemapSendMessage(
        base_url='https://scrummasterbot.herokuapp.com/images/planning_poker',
        alt_text='planning poker',
        base_size=BaseSize(height=790, width=1040))
    actions=[]
    location=0
    for i in range(0, 3):
        for j in range(0, 4):
            actions.append(MessageImagemapAction(
                text = u'#' + number + u' ' + str(location).encode('utf-8'),
                area=ImagemapArea(
                    x=j * POKER_IMAGEMAP_ELEMENT_WIDTH,
                    y=i * POKER_IMAGEMAP_ELEMENT_HEIGHT,
                    width=(j + 1) * POKER_IMAGEMAP_ELEMENT_WIDTH,
                    height=(i + 1) * POKER_IMAGEMAP_ELEMENT_HEIGHT
                )
            ))
            location+=1
    message.actions = actions
    return message

