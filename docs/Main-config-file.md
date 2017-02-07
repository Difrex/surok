# Surok main config file (0.8.x)

Default location is **/etc/surok/conf/surok.json**

```
{
    "version": "0.8"
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

## Config file options
* **version** - *string. Optional. "0.7" by default.*
Config files and templates version. Accept "0.7" or "0.8".
  * "0.7" - config files <= 0.7.х version
  * "0.8" - >= 0.8.x config files version

##### 0.8 version
* **marathon**, **mesos**, **consul**, **memcached** - *dict/hash. Optional. '{"enable":false}'. by default*
Surok working with folowing systems. If system is disabled parameters will be ignored.
  * **enable** - *boolean. Optional. false by default*
    Enable/disable system for usage.

    Specific variables:
    * For Marathon API "marathon"
      * **force** - *boolean. Optional. true by default*
        Force restart container over API.
      * **restart** - *boolean. Optional. false by default*
        Enable/disable restarting container
      * **host** - *string. Optional. "http://marathon.mesos:8080" by default*
        Marathon address.
    * For Consul "consul"
      * **domain** - *string. Required.*
        Consul private domain
    * For mesos-dns "mesos"
      * **domain** - *string. Optional. "marathon.mesos" by default*
        mesos-dns private domain
    * For Memcached "memcached"
      * **hosts** - memcached hosts
      * **discovery**
        * **enabled** - boolean. Enable/disable disovery memcached service
        * **service** - string. memcached app name
        * **group** - string. memcached app group
* **default_discovery** - *string. Optional. "mesos_dns" by default*
  Accept values:
  * "mesos_dns" - mesos-dns
  * "marathon_api"- Marathon API
  * "consul_dns" - Consul
* **confd** - *strig. Required.*
  Path to directory with app config files.
* **wait_time** - *int. Required.*
  Time in seconds how much Surok waits before starting to re-do the requests for service discovery
* **lock_dir** - *string. Required.*
  Path to directory where Surok write lock-files.
* **loglevel** - *string. Optional. "info" by default*
  Logleve. Accept values: "debug", "info", "warning", "error"

##### < 0.8 versions

* **marathon**
  * **enabled** - boolean. Enable/disable container restart. Renamed to "restart" in 0.8 version.
* **domain** - string. mesos-dns private domain. Moved to "mesos" hashtable in 0.8 version.
  Discovery over mesos-dns enabled all times.
