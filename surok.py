#!/usr/bin/python3

from time import sleep
import argparse
from surok.apps import Apps
from surok.config import Config

logger = Logger()

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='surok.json path')
args = parser.parse_args()

# Load base configurations
config = Config(args.config if args.config else '/etc/surok/conf/surok.json')

# Main loop
apps = Apps()
while 1:
    apps.update_()
    sleep(config['wait_time'])
