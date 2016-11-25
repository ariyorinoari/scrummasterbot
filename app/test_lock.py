import redis
import unittest

from lock import Lock

class TestLock(unittest.TestCase):

    _REDIS_URL = 'redis://192.168.99.100:6379'
    _KEY = 'LOCK'

    def setUp(self):
        self.redis = redis.from_url(TestLock._REDIS_URL)
        self.lock = Lock(self.redis, TestLock._KEY)

    def tearDonw(self):
        lock = self.lock
        if is_lock:
            self._redis.delete(TesetLock._KEY)

    def test_is_lock(self):
        lock = self.lock
        lock.lock()
        self.assertTrue(lock.is_lock())
        lock.unlock()
        self.assertFalse(lock.is_lock())

    def test_unlock(self):
        lock = self.lock
        lock.lock()
        self.assertIsNotNone(lock._redis.get(lock._key))
        lock.unlock()

if __name__ == '__main__':
    unittest.main()
