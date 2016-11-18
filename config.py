# -*- coding: utf-8 -*-

import os
import sys

DEBUG = True

# get channel_secret and channel_access_token from your environment variable
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
database_url = os.getenv('DATABASE_URL', None)
if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if database_url is None:
    print('Specify DATABASE_URL as environment variable.')
    sys.exit(1)

