import dns.resolver

def resolve(app, conf):
    hosts = {}
    services = app['services']
    domain = conf['domain']
    for service in services:
        hosts[service['name']] = []
        try:
            for rdata in dns.resolver.query('_' + service['name'] + '.' + service['group'] + '._tcp.' + domain, 'SRV'):
                info = str(rdata).split()
                server = { 'name': info[3], 'port': info[2] }

                hosts[ service['name'] ].append(server)
        except Exception as e:
            print("Could not resolve " + service['name'] + '.' + service['group'] + '._tcp.' + domain)

    return hosts
