# Surok main config file

Default location is /etc/surok/conf/surok.json

conf/surok.json
```
{
    "marathon": {
        "enabled": false,
        "restart": false,
        "force": true,
        "host": "http://marathon.mesos:8080"
    },
    "consul": {
        "enabled": false,
        "domain": "service.dc1.consul"
    },
    "mesos":{
        "enabled": true,
        "domain": "marathon.mesos"
    },
    "default_discovery": "mesos_dns",
    "confd": "/etc/surok/conf.d",
    "wait_time": 20,
    "lock_dir": "/var/tmp",
    "loglevel": "info",
    "container": false,
    "memcached": {
        "enabled": false,
        "discovery": {
            "enabled": false,
            "service": "memcached",
            "group": "system"
        },
        "hosts": ["localhost:11211"]
    }
}
```
* **marathon section**. Restarting app over marathon api if config changed. Disabled by default.
* **confd**. Directory where located configs apps.
* **domain**. Domain served by mesos-dns.
* **lock_dir**. Directory where surok writes temporary configs after resolving.
* **wait_time**. Sleep time in main loop.
* **container**. Not implemented.
* **memcached section**. Memcached support. Disabled by default.
