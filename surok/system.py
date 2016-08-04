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


def do_reload(service_conf, app_conf):
    print( 'Write new configuration of ' + app_conf['conf_name'] )

    f = open(app_conf['dest'], 'w')
    f.write(service_conf)
    f.close()

    write_lock(app_conf['conf_name'], service_conf)

    # Reload conf
    stdout = os.popen(app_conf['reload_cmd']).read()
    return stdout


def reload_conf(service_conf, app_conf, first):
    
    # Check first loop
    if first == True:
        stdout = do_reload(service_conf, app_conf)
        first = False
        return stdout, first

    if get_old(app_conf['conf_name'], service_conf) != 1:
        stdout = do_reload(service_conf, app_conf)
        return stdout, first
    else:
        return 'Same config ' + app_conf['conf_name'] + ' Skip reload', first
