# -*- coding: utf-8 -*-

import unittest

import sys

from app import *
from test import *

if __name__ == "__main__":
    lock = unittest.TestLoader().loadTestsFromTestCase(TestLock)
    suite = unittest.TestSuite([lock])
    unittest.TextTestRunner(verbosity=2).run(suite)

