import dns.resolver
import dns.query
from dns.exception import DNSException
from .logger import info, warning, error, debug
import sys


# Resolve service from mesos-dns SRV record
# return dict {"servicename": [{"name": "service.f.q.d.n.", "port": 9999}]}
def resolve(app, conf):
    hosts = {}
    services = app['services']
    domain = conf['domain']

    for service in services:
        hosts[service['name']] = {}
            
        group = get_group(service, app)
        if group is False:
            error('Group is not defined in config, SUROK_DISCOVERY_GROUP and MARATHON_APP_ID')
            error('Not in Mesos launch?')
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

        # Discovery over Consul DNS
        if 'consul' in conf and conf['consul']['enabled']:
            fqdn = '_' + service['name'] + '._tcp.' + conf['consul']['domain']
            hosts[service['name']] = do_query(fqdn, conf['loglevel'])
            continue
        
        if ports is not None:
            for port_name in ports:
                fqdn = '_' + port_name + '.' + '_' + service['name'] + '.' + group + '._tcp.' + domain
                hosts[service['name']][port_name] = do_query(fqdn, conf['loglevel'])
        else:
            fqdn = '_' + service['name'] + '.' + group + '._tcp.' + domain
            hosts[service['name']] = do_query(fqdn, conf['loglevel'])

    return hosts


# Do DNS queries
# Return array:
# [{"name": "f.q.d.n", "port": 8876, "ip": ["10.10.10.1", "10.10.10.2"]}]
def do_query(fqdn, loglevel):
    servers = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 1
        resolver.timeout = 1
        query = resolver.query(fqdn, 'SRV')
        for rdata in query:
            info = str(rdata).split()
            name = info[3][:-1]
            port = info[2]
            server = {'name': name, 'port': port, 'ip': []}
            a_query = resolver.query(name, 'A')
            for a_rdata in a_query:
                server['ip'].append(a_rdata.address)
                servers.append(server)
    except DNSException as e:
        if loglevel != 'info':
            error("Could not resolve " + fqdn)

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
    del(marathon_app_id[-1])
    marathon_app_id.reverse()
    group = ".".join(marathon_app_id)[:-1]
    return(group)
