import sys
from time import time


def make_message(message):
    cur_time = str(time())
    m = '[' + cur_time + '] ' + message['level'] + ': ' + message['raw'] + "\n"
    return m


def info(message):
    req = {'level': 'INFO', 'raw': message}
    m = make_message(req)

    sys.stdout.write(m)


def warning(message):
    req = {'level': 'WARNING', 'raw': message}
    m = make_message(req)

    sys.stderr.write(m)


def error(message):
    req = {'level': 'ERROR', 'raw': message}
    m = make_message(req)

    sys.stderr.write(m)


def debug(message):
    req = {'level': 'DEBUG', 'raw': message}
    m = make_message(req)

    sys.stderr.write(m)
