# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time

from datetime import datetime
import lock 

class Lock(object):

    def __init__(self, redis, key):
        self._lock = False
        self._redis = redis
        self._key = key


    def _get_now(self):
            return float(datetime.now().strftime('%s.%f'))


    def is_lock(self):
        return self._lock


    def lock(self):
        # すでにロック済みの場合
        if self._lock:
            raise DuplicateLockError()

        self._lock = self._redis.setnx(self._key, self._get_now())
        return self._lock


    def unlock(self):
        if not self._lock:
            raise HasNotLockError()

        self._redis.delete(self._key)
        self._lock = False


    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, type, value, traceback):
        if self._lock:
            self.unlock()
        return True if type is None else False


class LockError(Exception):
    pass


class HasNotLockError(LockError):
    pass

class DuplicateLockError(LockError):
    pass

