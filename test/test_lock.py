import redis
import sys
import time
import unittest
from multiprocessing import Process

from app.lock import Lock, DuplicateLockError, HasNotLockError

class TestLock(unittest.TestCase):

    _REDIS_URL = 'redis://192.168.99.100:6379'
    _KEY = 'LOCK'

    def setUp(self):
        self.redis = redis.from_url(TestLock._REDIS_URL)
        self.lock = Lock(self.redis, TestLock._KEY)

    def tearDown(self):
        lock = self.lock
        if lock.is_lock():
            self.redis.delete(TestLock._KEY)

    def test_initial_lock_state(self):
        lock = self.lock
        self.assertFalse(lock.is_lock())

    def test_lock_is_success(self):
        lock = self.lock
        lock.lock()
        result = self.redis.get(TestLock._KEY)
        self.assertIsNotNone(result)

    def test_duplicate_lock_error(self):
        lock = self.lock
        lock.lock()
        result = self.redis.get(TestLock._KEY)
        self.assertIsNotNone(result)

        with self.assertRaises(DuplicateLockError):
            lock.lock()

    def test_is_lock(self):
        lock = self.lock
        lock.lock()
        self.assertTrue(lock.is_lock())
        lock.unlock()
        self.assertFalse(lock.is_lock())

    def test_unlock(self):
        lock = self.lock
        lock.lock()
        self.assertTrue(lock.is_lock())
        lock.unlock()
        self.assertFalse(lock.is_lock())
        result = self.redis.get(TestLock._KEY)
        self.assertIsNone(result)

    def test_has_not_lock_error(self):
        lock = self.lock

        with self.assertRaises(HasNotLockError):
            lock.unlock()

    def test_multi_process(self):
        lock = self.lock

        def lock_success(self):
            r = redis.from_url(TestLock._REDIS_URL)
            l = Lock(self.redis, TestLock._KEY)
            l.lock()
            self.assertTrue(l.is_lock())
            time.sleep(10)
            l.unlock()

        def lock_error(self):
            r = redis.from_url(TestLock._REDIS_URL)
            l = Lock(self.redis, TestLock._KEY)
            l.lock()
            self.assertFalse(l.is_lock())

        jobs = [
            Process(target=lock_success, args=(self, )),
            Process(target=lock_error, args=(self, ))
        ]

        for i in jobs:
            i.start()

        for i in jobs:
            i.join()

if __name__ == '__main__':
    unittest.main()

