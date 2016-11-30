#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import errno
import logging
import os
import re
import redis
import time

from flask_sqlalchemy import SQLAlchemy
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

import const

from utility import *
from mutex import Mutex

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
redis = redis.from_url(app.config['REDIS_URL'])
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(app.config['LOG_LEVEL'])
make_static_dir(const.TMP_ROOT_PATH)
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
    filename = const.POKER_IMAGE_FILENAME.format(size)
    return send_from_directory(os.path.join(app.root_path, 'static/planning_poker/'),
            filename)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    sourceId = getSourceId(event.source)
    matcher = re.match(r'^#(\d+) (.+)', text)

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

with app.test_request_context():
    print url_for('download_imagemap', size='240')


def genenate_voting_result_message(key):
    data = redis.hgetall(key)
    tmp = generate_voting_result_image(data)
    buttons_template = ButtonsTemplate(
        title='ポーカー結果',
        text='そろいましたか？',
        thumbnail_image_url='https://scrummasterbot.herokuapp.com/images/tmp/' + tmp + '/result_11.png',
        actions=[
            MessageTemplateAction(label='もう１回', text='プラポ'),
            MessageTemplateAction(label='やめる', text='やめる'),
    ])
    template_message = TemplateSendMessage(
        alt_text='結果', template=buttons_template)
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
