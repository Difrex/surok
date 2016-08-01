import os


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


def reload_conf(service_conf, app_conf):
    
    # Check old config
    if get_old(app_conf['name'], service_conf) != 1:
        print('Write new configuration')

        f = open(app_conf['dest'], 'w')
        f.write(service_conf)
        f.close()

        write_lock(app_conf['name'], service_conf)

        # Reload conf
        stdout = os.popen(app_conf['reload_cmd']).read()
        return stdout
    else:
        return 'Same config. Skip reload'
