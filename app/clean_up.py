#-*- coding: utf-8 -*-

import logging
import os
import shutil
import sys

from datetime import datetime, timedelta
from logging import Formatter
from werkzeug.utils import import_string

from const import *

logger = logging.getLogger('cleaner')
logger.setLevel(logging.INFO)
formatter = Formatter('%(asctime)s- %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %p %I:%M:%S')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

def clean_up_tmp_files():
    logger.info('clean up temporarry files')
    dirs = os.listdir(TMP_ROOT_PATH)

    for d in dirs:
        path = os.path.join(TMP_ROOT_PATH, d)
        if os.path.isdir(path):
            created = datetime.fromtimestamp(os.stat(path).st_mtime)
            if created < (_current_timestamp() + timedelta(hours=-1)):
                logger.info(path)
                shutil.rmtree(path)

def _current_timestamp():
    return datetime.now()

if __name__ == '__main__':
    clean_up_tmp_files()

