# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time

from datetime import datetime
import lock 

class Lock(object):

    def __init__(self, redis, key, expire=0):
        # lock status
        self._lock = False
        # redis client
        self._redis = redis
        # lock key
        self._key = key
        # duration
        self._expire = expire


    def _get_now(self):
            return float(datetime.now().strftime('%s.%f'))


    def is_lock(self):
        return self._lock


    def lock(self):
        # すでにロック済みの場合
        if self._lock:
            raise

        self._lock = self._redis.setnx(self._key, self._get_now() + self._expire)
        # ロックを獲得できなかった場合
        if not self._lock:
            previous_expire = self._redis.get(self._key)
            if previous_expire is None:
                raise
            if previous_expire < self._get_now():
                self._lock = self._r.getset(self._key, self._get_now() + self._expire)


    def unlock(self):
        if not self._lock:
            raise HasNotLockError()

        self._redis.delete(self._key)
        self._lock = False


class LockError(Exception):
    pass


class HasNotLockError(LockError):
    pass

