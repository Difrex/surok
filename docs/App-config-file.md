# Surok app config file

conf.d/myapp.json
```
{
    "services": [
      {
        "name": "myapp",
        "group": "backend.production",
        "ports": ["proxy", "api"]
      },
      {
        "name": "nginx",
        "group": "frontend.production"
      }
    ],
    "conf_name": "myapp_backend_production",
    "template": "/etc/surok/templates/myapp.jj2",
    "dest": "/etc/myapp/myapp.cfg",
    "reload_cmd": "killall -9 myapp; /usr/local/bin/myapp -config /etc/myapp/myapp.cfg"
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
