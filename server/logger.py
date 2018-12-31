#!/usr/bin/env python3
# License: GPL-3.0

from datetime import datetime
from server.config import LOG_FILE

def log_time():
    return datetime.now().strftime('%m-%d-%Y_%H:%M:%S')

def logger(msg):
    LogFile = open(LOG_FILE, 'a')
    LogFile.write("[{}] - {}\n".format(log_time(), str(msg)))
    LogFile.close()
