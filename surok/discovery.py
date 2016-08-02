import dns.resolver

def resolve(app, conf):
    hosts = []
    services = app['services']
    domain = conf['domain']
    for service in services:
        for rdata in dns.resolver.query('_' + service['name'] + '.' + service['group'] + '._tcp.' + domain, 'SRV'):
            info = str(rdata).split()
            server = { service['name']: { 'name': info[3], 'port': info[2] } }
            hosts.append(server)

    return hosts
