# -*- coding:utf-8 -*-

def getSourceId(source):
    sourceType = source.type
    if sourceType == 'user':
        return source.user_id
    elif sourceType == 'group':
        return source.group_id
    elif sourceType == 'room':
        return source.room_id
    else:
        raise NotFoundSourceError()

class NotFoundSourceError(Exception):
    pass
