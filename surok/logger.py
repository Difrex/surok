import sys
import json
from time import time
_loglevel='info'
msg_level={'debug':'DEBUG',
           'info':'INFO',
           'warning':'WARNING',
           'error':'ERROR'}

class Logger:
    def __init__(self,*args):
        if args:
            self.set_level(args[0])

    def set_level(self,level):
        if level in ['debug','info','warning','error']:
            global _loglevel
            _loglevel=level

    def get_level(self):
        return _loglevel

    def __make_message(self,message):
        r=[]
        l=self.get_level()
        for m in message:
            if type(m).__name__=='str':
                r.append(m)
            else:
                r.append(json.dumps(m,sort_keys=True,indent=2))
        return '[' + str(time()) + '] ' + msg_level[l] + ': ' + ''.join(r) + "\n"

    def debug(self,*message):
        if self.get_level() in ['debug']:
            sys.stderr.write(self.__make_message(message))

    def info(self,*message):
        if self.get_level() in ['debug','info']:
            sys.stdout.write(self.__make_message(message))

    def warning(self,*message):
        if self.get_level() in ['debug','info','warning']:
            sys.stderr.write(self.__make_message(message))

    def error(self,*message):
        sys.stderr.write(self.__make_message(message))

    def testing(self,level,message):
        self.set_level(level)
        return self.__make_message(message)

