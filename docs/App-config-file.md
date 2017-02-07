# Surok app config file

conf.d/myapp.json
```
{
    "services": [
      {
        "name": "kioskservice",
        "group": "production.romania",
        "ports": ["web", "socket"]
      }
    ],
    "discovery": "mesos_dns",
    "group": "dev.web",
    "conf_name": "kiosk",
    "template": "/etc/surok/templates/kiosk.jj2",
    "dest": "/etc/nginx/sites-available/kioskservice.conf",
    "reload_cmd": "/sbin/nginx -t && /bin/systemctl reload nginx",
    "run_cmd": ["/usr/bin/node", "-c", "config.json"]
}
```
* **services**. List of hashes with required services for app.
  1. _name_ - string. App name in Marathon. If you use a Marathon discovery, you can use the "*" at the end of the string to indicate any character.
  2. _group_ - string. App group in Marathon. Optional. Discovery policy: 1) config 2) SUROK_DISCOVERY_GROUP environment variable 3) Marathon API
  3. _ports_ - list. Name of opened port. In marathon of course. If you use a Marathon discovery, you can use the "*" at the end of the string to indicate any character. Optional.
* **conf_name**. Unique app config name.
* **template**. Jinja2 template location.
* **dest**. Destination config path.
* **reload_cmd**. Command to execute if generated config is changed.
* **discovery**. Use custom discovery for app. 
* **group**. Default group for all required services.
