# Public names
__all__ = ['Logger']

import sys
import json
import time


class Logger:

    """ Public Logger oblect
    ==================================================
    .set_level(level) - set level messages
        level - values 'debug', 'info', 'warning', 'error'
        * error - write error message
        * warning - write warning and error message
        * info - write info, warning and error message
        * debug - write all message
    .get_level() - get level messages
    .error(str) - write error message
    .warning(str) - write warning message
    .info(str) - write info message
    .debug(str)- write error message
    """
    _instance = None
    _loglevel = 'info'
    _msg_level = {
        'debug': 'DEBUG',
           'info': 'INFO',
        'warning': 'WARNING',
          'error': 'ERROR'
    }

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args):
        if args:
            self.set_level(args[0])

    def set_level(self, level):
        if level in ['debug', 'info', 'warning', 'error']:
            self._loglevel = level
            return True
        else:
            self.warning('Log level "', level, '" not valid')
            return False

    def get_level(self):
        return self._loglevel

    def _make_message(self, level, message):
        r = []
        for m in message:
            if type(m).__name__ == 'str':
                r.append(m)
            else:
                r.append(json.dumps(m, sort_keys=True, indent=2))
        return "[ {0} ] {1}: {2}\n".format(str(time.time()), self._msg_level[level], ''.join(r))

    def debug(self, *message):
        if self.get_level() in ['debug']:
            self._log2err(self._make_message('debug', message))

    def info(self, *message):
        if self.get_level() in ['debug', 'info']:
            self._log2out(self._make_message('info', message))

    def warning(self, *message):
        if self.get_level() in ['debug', 'info', 'warning']:
            self._log2out(self._make_message('warning', message))

    def error(self, *message):
        self._log2err(self._make_message('error', message))

    def _log2err(self, out):
        sys.stderr.write(out)

    def _log2out(self, out):
        sys.stdout.write(out)
