import dns.resolver
import dns.query
from dns.exception import DNSException
import logging
import sys


# Logger configuration
# This need to be moved
def get_logger():
    # Configure logging
    FORMAT = '%(asctime) %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger(__name__)
    return logger


# Resolve service from mesos-dns SRV record
# return dict {"servicename": [{"name": "service.f.q.d.n.", "port": 9999}]}
def resolve(app, conf):
    hosts = {}
    services = app['services']
    domain = conf['domain']
    logger = get_logger()

    for service in services:
        hosts[service['name']] = {}

        group = get_group(service, app)
        if group is False:
            logger.error('Group is not defined in config, SUROK_DISCOVERY_GROUP and MARATHON_APP_ID')
            logger.error('Not in Mesos launch?')
            sys.exit(2)
        
        # Port name from app config
        ports = None
        try:
            ports = service['ports']
        except:
            pass

        # This is fast fix for port naming
        # Will be rewrite later
        fqdn = ''
        if ports is not None:
            for port_name in ports:
                fqdn = '_' + port_name + '.' + '_' + service['name'] + '.' + group + '._tcp.' + domain
                hosts[service['name']][port_name] = do_query(fqdn, conf['loglevel'])
        else:          
            fqdn = '_' + service['name'] + '.' + group + '._tcp.' + domain
            hosts[service['name']] = do_query(fqdn, conf['loglevel'])

    return hosts


# Do SRV queries
# Return array: [{"name": "f.q.d.n", "port": 8876}]
def do_query(fqdn, loglevel):
    logger = get_logger()
    servers = []
    try:
        query = dns.resolver.query(fqdn, 'SRV')
        query.lifetime = 1.0

        for rdata in query:
            info = str(rdata).split()
            server = {'name': info[3][:-1], 'port': info[2]}
            servers.append(server)
    except DNSException as e:
        if loglevel != 'info':
            logger.error("Could not resolve " + fqdn + ': ' + str(e))

    return servers


# Groups switch
# Priority: config, environment, marathon environment
def get_group(service, app):
    # Check group in app conf
    if 'group' in service:
        return service['group']
    # Check environment variable
    elif app['env'].get('SUROK_DISCOVERY_GROUP'):
        return app['env']['SUROK_DISCOVERY_GROUP']
    # Check marathon environment variable
    elif app['env'].get('MARATHON_APP_ID'):
        group = parse_marathon_app_id(app['env']['MARATHON_APP_ID'])
        return group
    else:
        return False


# Parse MARATHON_APP_ID
# Return marathon.group
def parse_marathon_app_id(marathon_app_id):
    marathon_app_id = marathon_app_id.split('/')
    group = ''
    counter = len(marathon_app_id) - 2
    i = 0
    while counter > i:
        group = group + marathon_app_id[counter]
        if counter != i + 1:
            group += '.'
        counter -= 1

    return group
