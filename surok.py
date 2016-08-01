#!/usr/bin/python3

from time import sleep
from os import listdir
from os.path import isfile, join 
import json

# Load base configurations
f = open('conf/surok.json', 'r')
conf = json.loads(f.read())
print(conf)


# Get app configurations 
def get_configs():
    confs = [f for f in listdir(conf['confd']) if isfile(join(conf['confd'], f))]
    return confs


# Main loop
while 1:
    confs = get_configs()
    for i in confs:
        print(i)
    sleep(5)

