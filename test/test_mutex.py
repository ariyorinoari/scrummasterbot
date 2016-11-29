import redis
import sys
import time
import unittest
from multiprocessing import Process

from app.mutex import Mutex, DuplicateLockError, HasNotLockError

class TestMutex(unittest.TestCase):

    REDIS_URL = 'redis://192.168.99.100:6379'
    KEY = 'LOCK'

    def setUp(self):
        self.redis = redis.from_url(TestLock.REDIS_URL)
        self.mutex= Mutex(self.redis, TestLock.KEY)

    def tearDown(self):
        mutex = self.lock
        if mutex.is_lock():
            self.redis.delete(TestLock._KEY)

    def test_initial_lock_state(self):
        mutex = self.mutex
        self.assertFalse(mutex.is_lock())

    def test_lock_is_success(self):
        mutex = self.mutex
        mutex.lock()
        result = self.redis.get(TestLock._KEY)
        self.assertIsNotNone(result)

    def test_duplicate_lock_error(self):
        mutex = self.mutex
        mutex.lock()
        result = self.redis.get(TestLock._KEY)
        self.assertIsNotNone(result)

        with self.assertRaises(DuplicateLockError):
            mutex.lock()

    def test_is_lock(self):
        mutex = self.mutex
        mutex.lock()
        self.assertTrue(mutex.is_lock())
        mutex.unlock()
        self.assertFalse(mutex.is_lock())

    def test_unlock(self):
        mutex = self.mutex
        mutex.lock()
        self.assertTrue(mutex.is_lock())
        mutex.unlock()
        self.assertFalse(mutex.is_lock())
        result = self.redis.get(TestLock._KEY)
        self.assertIsNone(result)

    def test_has_not_lock_error(self):
        mutex = self.mutex

        with self.assertRaises(HasNotLockError):
            mutex.unlock()

    def test_multi_process(self):
        mutex = self.mutex

        def lock_success(self):
            r = redis.from_url(TestLock._REDIS_URL)
            m = Mutex(self.redis, TestLock._KEY)
            m.lock()
            self.assertTrue(m.is_lock())
            time.sleep(10)
            m.unlock()

        def lock_error(self):
            r = redis.from_url(TestLock._REDIS_URL)
            m = Mutex(self.redis, TestLock._KEY)
            m.lock()
            self.assertFalse(m.is_lock())

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

