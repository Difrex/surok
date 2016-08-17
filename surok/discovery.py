import dns.resolver
import dns.query
from dns.exception import DNSException
import logging


# Resolve service from mesos-dns SRV record
# return dict {"servicename": [{"name": "service.f.q.d.n.", "port": 9999}]}
def resolve(app, conf):
    hosts = {}
    services = app['services']
    domain = conf['domain']
    group = None

    # Groups hack
    if app['env'].get('SUROK_DISCOVERY_GROUP') is not None:
        group = app['env']['SUROK_DISCOVERY_GROUP']

    for service in services:
        hosts[service['name']] = []

        # Check group configuration
        if group is not None:
            pass
        else:
            # Load group from service config
            # /etc/surok/conf.d/service_conf.json
            group = service['group']

        # Port name from app config
        port_name = None
        try:
            port_name = service['port_name']
        except:
            pass

        # This is fast fix for port naming
        # Will be rewrite later
        fqdn = ''
        if port_name is not None:
            fqdn = '_' + port_name + '.' + '_' + service['name'] + '.' + group + '._tcp.' + domain
        else:
            fqdn = '_' + service['name'] + '.' + group + '._tcp.' + domain

        hosts[service['name']] = do_query(fqdn, conf['loglevel'])

    return hosts


# Do SRV queries
# Return array: [{"name": "f.q.d.n", "port": 8876}]
def do_query(fqdn, loglevel):
    servers = []
    try:
        query = dns.resolver.query(fqdn, 'SRV')
        query.lifetime = 1.0

        for rdata in query:
            info = str(rdata).split()
            server = {'name': info[3][:-1], 'port': info[2]}
            servers.append(server)
    except DNSException:
        if loglevel != 'info':
            logging.warning("Could not resolve " + fqdn)

    return servers
