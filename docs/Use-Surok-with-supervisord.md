# Use Surok with supervisord

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Use Surok with supervisord](#use-surok-with-supervisord)
    - [supervisord.conf](#supervisordconf)
    - [surok service conf](#surok-service-conf)
    - [install supervisord in you container and set it as entrypoint](#install-supervisord-in-you-container-and-set-it-as-entrypoint)

<!-- markdown-toc end -->


## supervisord.conf
Write supervisord.conf. Example:
```ini
[unix_http_server]
file=/tmp/supervisor.sock

[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10           ; (num of main logfile rotation backups;default 10)
loglevel=info                ; (log level;default info; others: debug,warn,trace)
pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=true               ; (start in foreground if true;default false)
minfds=1024                  ; (min. avail startup file descriptors;default 1024)
minprocs=200

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[program:surok]
command=/usr/bin/python3 /opt/surok/surok.py -c /etc/surok/conf/surok.json

[program:my_service]
command=/app/my_service -conf /app/conf/my_service.conf
user=www-data
startsecs=2
```

## surok service conf
Write /etc/surok/conf.d/my_service.json config like that
```json
{
    "services": [
      {
	"name": "my-service",
        "group": "production.web"
      }

    ],
    "conf_name": "my_service",
    "template": "/etc/surok/templates/my-service.jj2",
    "dest": "/app/conf/my_service.conf",
    "reload_cmd": "/usr/bin/supervisorctl restart my_service"
}
```

## install supervisord in you container and set it as entrypoint
```dockerfile
...
# Install supervisord and provide config
RUN easy_install supervisor
ADD supervisord.conf /etc

ENTRYPOINT /usr/bin/supervisord -c /etc/supervisord.conf
```
