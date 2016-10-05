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
        hosts[service['name']] = {}

        # Check group configuration
        if group is not None:
            pass
        else:
            # Load group from service config
            # /etc/surok/conf.d/service_conf.json
            group = service['group']

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

                # Fast fix of empty query result
                # ------------------------------
                try:
                    do_query_test = do_query(fqdn, conf['loglevel'])
                    if do_query_test['state'] == 404:
                        return 404
                except:
                    pass
                # ------------------------------

                hosts[service['name']][port_name] = do_query(fqdn, conf['loglevel'])
        else:

            # Fast fix of empty query result
            # ------------------------------
            try:
                do_query_test = do_query(fqdn, conf['loglevel'])
                if do_query_test['state'] == 404:
                    return 404
            except:
                pass
            # ------------------------------
            
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
    except DNSException as e:
        if loglevel != 'info':
            logging.error("Could not resolve " + fqdn + ': ' + str(e))
            return {"state": 404}

    return servers
