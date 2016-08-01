import os

def reload_conf(service_conf, app_conf):
    f = open(app_conf['dest'], 'w')
    f.write(service_conf)
    f.close()

    # Reload conf
    stdout = os.popopen(app_conf['reload_cmd']).read()
    return stdout
