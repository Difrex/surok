#!/usr/bin/python3

import os
import subprocess
from time import sleep
import sys


def child():
    bashCommand = "./b.sh"
    process = subprocess.Popen(bashCommand, stdout=sys.stdout)
    # output = process.communicate()

    return process


def parent():
    newpid = os.fork()
    if newpid == 0:
        child()
    else:
        pids = (os.getpid(), newpid)
        print("parent: %d, child: %d\n" % pids)

    c = 0
    while c < 5:
        sleep(2)
        p = open('/var/tmp/surok.spid')
        cpid = p.read()
        p.close()
        print(cpid, c)
        c = c + 1

parent()
