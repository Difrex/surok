import dns.resolver

def resolve(app, conf):
    hosts = []
    domain = conf['domain']
    for rdata in dns.resolver.query('_' + app['name'] + '.' + app['group'] + '._tcp.' + domain, 'SRV'):
        info = str(rdata).split()
        server = { 'name': info[3], 'port': info[2] }
        hosts.append(server)

    return hosts
