# -*- coding: utf-8 -*-

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

class Poker(object):

    def __init__(self, redis, sourceId):
        self._redis = redis
        self._id = str(redis.incr(sourceId)).encode('utf-8')

    def generatePlanningPokerMessage(self):
        message = ImagemapSendMessage(
            base_url='https://scrummasterbot.herokuapp.com/images/planning_poker',
            alt_text='this is planning poker',
            base_size=BaseSize(height=790, width=1040),
            actions=[
                MessageImagemapAction(
                    text = u'#' + self._id + u' 0',
                    area=ImagemapArea(
                        x=0, y=0, width=260, height=260
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 1',
                    area=ImagemapArea(
                        x=260, y=0, width=515, height=260
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 2',
                    area=ImagemapArea(
                        x=520, y=0, width=770, height=260
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 3',
                    area=ImagemapArea(
                        x=720, y=0, width=1040, height=260
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 4',
                    area=ImagemapArea(
                        x=0, y=260, width=260, height=520
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 5',
                    area=ImagemapArea(
                        x=260, y=260, width=515, height=520
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 6',
                    area=ImagemapArea(
                        x=520, y=260, width=770, height=520
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 7',
                    area=ImagemapArea(
                        x=720, y=260, width=1040, height=520
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 8',
                    area=ImagemapArea(
                        x=0, y=520, width=260, height=790
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 9',
                    area=ImagemapArea(
                        x=260, y=520, width=515, height=790
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 10',
                    area=ImagemapArea(
                        x=520, y=520, width=770, height=790
                    )
                ),
                MessageImagemapAction(
                    text = u'#' + self._id + u' 11',
                    area=ImagemapArea(
                        x=720, y=520, width=1040, height=790
                    )
                )
            ]
        )
        return message
