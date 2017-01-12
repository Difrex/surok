# Templates

Surok using Jinja2 for templates. [Jinja2 documentation](http://jinja.pocoo.org/docs/dev/)

## my dictionary in templates

```
{
   "services": {
     "nginx": [
         {
          "name": "nginx.testing-kl92-s0.marathon.mesos.",
          "port": "31200",
          "ip": ["10.10.10.1"]
         },
         {
          "name": "nginx.testing-kl123-s1.marathon.mesos.",
          "port": "32230",
          "ip": ["10.10.10.2"]
         }
      ],
      "emailsender": [
         {
          "name": "emailsender.testing-kl92-s0.marathon.mesos.",
          "port": "31201",
          "ip": ["10.10.10.1"]
         },
         {
          "name": "emailsender.testing-kl123-s1.marathon.mesos.",
          "port": "32232",
          "ip": ["10.10.10.1"]
         }
      ],
     "service-with-defined-ports": {
         "web": [
           {
             "name": "f.q.d.n",
             "port": 12341
           }
         ],
         "rpc": [
           {
             "name": "f.q.d.n",
             "port": 12342
           }
         ]
     }
   },
   "env": {
      "HOME": "/var/lib/nginx"
   }
}
```

## Real template example

nginx config
```
upstream matrix-http {
    hash $remote_addr;
{% for server in my['services']['matrix']['http'] %}
    server {{server['name']}}:{{server['port']}} max_fails=3;
{% endfor %}
}
 
upstream riot-http {
    hash $remote_addr;
{% for server in my['services']['riot'] %}
    server {{server['name']}}:{{server['port']}} max_fails=3;
{% endfor %}
}
 
server {
    listen 10.15.56.157:80;
    server_name matrix.example.com;
 
    client_max_body_size 10m;
 
    location / {
        proxy_pass http://riot-http;
        proxy_set_header  X-Real-IP        $remote_addr;
        proxy_set_header  Host             $http_host;
        proxy_set_header  X-Forwarded-For  $proxy_add_x_forwarded_for;
    }
 
    location /_matrix/ {
        proxy_pass http://matrix-http;
        proxy_set_header  X-Real-IP        $remote_addr;
        proxy_set_header  Host             $http_host;
        proxy_set_header  X-Forwarded-For  $proxy_add_x_forwarded_for;
    }
 
}
```

## Checks in template

_my['env']_ is a python os.environ class. Look bellow:
```
{% if my['env'].get('DB_HOST') %}
host = '{{my['env']['DB_HOST']}}'
{% else %}
host = 'localhost'
{% endif %}
```
