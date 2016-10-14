import os
import sys
import logging
import requests


# Get old configuration
def get_old(name, service_conf):

    try:
        path = '/var/tmp/surok.' + name
        f = open(path, 'r')
        old = f.read()
        f.close()
    except Exception as e:
        print(str(e))
        return 0

    if old == service_conf:
        return 1
    else:
        return 0


def write_lock(name, service_conf):
    path = '/var/tmp/surok.' + name
    f = open(path, 'w')
    f.write(service_conf)
    f.close()


def do_reload(service_conf, app_conf):
    logging.warning('Write new configuration of ' + app_conf['conf_name'])

    f = open(app_conf['dest'], 'w')
    f.write(service_conf)
    f.close()

    write_lock(app_conf['conf_name'], service_conf)

    # Reload conf
    stdout = os.popen(app_conf['reload_cmd']).read()
    return stdout


def reload_conf(service_conf, app_conf, first, conf):

    # Check first loop
    if first is True:
        stdout = do_reload(service_conf, app_conf)
        first = False
        logging.info(stdout)
        return first

    # Check marathon enabled in configuration
    if conf['marathon']['enabled'] is True:
        restart_self_in_marathon(conf['marathon'])
        
    if get_old(app_conf['conf_name'], service_conf) != 1:
        stdout = do_reload(service_conf, app_conf)
        logging.info(stdout)
        return first
    else:
        if conf['loglevel'] == 'debug':
            logging.debug('Same config ' +
                          app_conf['conf_name'] +
                          ' Skip reload')
        return first


# Do POST request to marathon API
# /v2/apps//app/name/restart
def restart_self_in_marathon(marathon):
    host = marathon['host']

    # Check MARATHON_APP_ID environment varible
    if os.environ.get('MARATHON_APP_ID') is not True:
        logging.error('Cannot find MARATHON_APP_ID. Not in Mesos?')
        sys.exit(2)
    app_id = os.environ['MARATHON_APP_ID']
    uri = 'http://' + host + '/v2/apps/' + app_id + '/restart'

    # Ok. In this step we made restart request to Marathon
    if marathon['force'] is True:
        r = requests.post(uri, data = {'force': 'true'})
    else:
        r = requests.post(uri, data = {})
    
