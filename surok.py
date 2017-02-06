#!/usr/bin/python3

from time import sleep
import os
from os import listdir
from os.path import isfile, join
import json
import argparse
from surok.templates import gen
from surok.discovery import Discovery
from surok.system import reload_conf
from surok.logger import Logger
from surok.config import Config

logger=Logger()

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='surok.json path')
args = parser.parse_args()

# Load base configurations
config=Config(args.config if args.config else '/etc/surok/conf/surok.json')

# Main loop
###########

discovery=Discovery()

while 1:
    # Update config from discovery object
    discovery.update_data()
    for app in config.apps:

        app_hosts = discovery.resolve(app)

        # Populate my dictionary
        my = {"services": app_hosts,
              "conf_name": app['conf_name']}

        logger.debug('my=',my)

        # Generate config from template
        service_conf = gen(my, app['template'])

        reload_conf(service_conf, app, config, app_hosts)

    sleep(config['wait_time'])
