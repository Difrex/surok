#!/usr/bin/python3

from time import sleep
from os import listdir
from os.path import isfile, join
import json
from surok.templates import gen
from surok.discovery import resolve
from surok.system import reload_conf

import argparse

# Load base configurations
surok_conf = '/etc/surok/conf/surok.json'

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config')
args = parser.parse_args()
if args.config:
        surok_conf = args.config

# Read config file
f = open(surok_conf, 'r')
conf = json.loads(f.read())
print(conf)
f.close()


# Get app configurations
# Return list of patches to app discovery configuration
def get_configs():
    confs = [f for f in listdir(conf['confd']) if isfile(
        join(conf['confd'], f))]
    return confs


# Get Surok App configuration
# Read app conf from file and return dict
def load_app_conf(app):
    f = open(conf['confd'] + '/' + app)
    c = json.loads(f.read())
    f.close()

    return c


# Main loop
###########

# Bad hack for detect first run
# On host system set it to False
# TODO: put it to config
first = True
while 1:
    confs = get_configs()
    for app in confs:
        app_conf = load_app_conf(app)

        # Resolve services
        app_hosts = resolve(app_conf, conf)

        # Populate my dictionary
        my = {"services": app_hosts,
              "conf_name": app_conf['conf_name']}

        # Generate config from template
        service_conf = gen(my, app_conf['template'])

        stdout, first = reload_conf(service_conf, app_conf, first)
        print(stdout)

    sleep(conf['wait_time'])
