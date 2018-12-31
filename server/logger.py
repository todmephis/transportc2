#!/usr/bin/env python3
# License: GPL-3.0

from datetime import datetime
from server.config import LOG_FILE

def log_time():
    return datetime.now().strftime('%m-%d-%Y_%H:%M:%S')

def logger(msg):
    # @TODO Create log folder/file if not exist (will break if log file changed in config)
    LogFile = open(LOG_FILE, 'a')
    LogFile.write("[{}] - {}\n".format(log_time(), str(msg)))
    LogFile.close()
