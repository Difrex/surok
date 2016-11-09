import os
import sys
import logging
import requests
import memcache


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


# Get old discovered servers from memcache
def get_old_from_memcache(mc, name, app_hosts):
    mc_servers_key = 'surok_' + name + '_servers'
    new_servers = []
    old_servers = mc.get(mc_servers_key)
    for service in app_hosts:
        for server in app_hosts[service]:
            new_servers.append(server['name'] + ':' + server['port'])

    for server in new_servers:
        if server not in old_servers:
            write_confs_to_memcache(mc, new_servers, mc_servers_key)
            return 0

    return 1


# Write to memcache
def write_confs_to_memcache(mc, servers, key):
    mc.set(key, servers)


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


# !!! NEED REFACTORING !!!
def reload_conf(service_conf, app_conf, conf, app_hosts):
    # Check marathon enabled in configuration
    if conf['marathon']['enabled'] is True:
        if get_old(app_conf['conf_name'], service_conf) != 1:
            restart_self_in_marathon(conf['marathon'])

    # Check memcache
    # Need rewriting
    ################
    if 'memcached' in conf:
        if conf['memcached']['enabled'] is True:
            # Check old servers
            if conf['memcached']['discovery']['enabled'] is True:
                logging.warning('Discovery of Memcached not implpemented')
            try:
                mc = memcache.Client(conf['memcached']['hosts'])
                if get_old_from_memcache(mc, app_conf['conf_name'], service_conf) != 1:
                    stdout = do_reload(service_conf, app_conf)
                    logging.info(stdout)
                    return True
            except Exception as e:
                logging.error('Cannot connect to memcached: ' + str(e))

    else:
        logging.warning('DEPRECATED main conf file. Please use new syntax!')
        # End of memcache block
        #######################

    if get_old(app_conf['conf_name'], service_conf) != 1:
        stdout = do_reload(service_conf, app_conf)
        logging.info(stdout)
        return True
    else:
        if conf['loglevel'] == 'debug':
            logging.debug('Same config ' +
                          app_conf['conf_name'] +
                          ' Skip reload')
        return False


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
        r = requests.post(uri, data = {'force': 'false'})
