# Templates

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Templates](#templates)
    - [my dictionary in templates](#my-dictionary-in-templates)
        - [0.8 version](#08-version)
            - [Real template example](#real-template-example)
            - [Checks in template](#checks-in-template)
        - [0.7 version](#07-version)
            - [Real template example](#real-template-example)

<!-- markdown-toc end -->


Surok using Jinja2 for templates. [Jinja2 documentation](http://jinja.pocoo.org/docs/dev/)

## my dictionary in templates

### 0.8 version

```
{
   "services": {
     "asterisk": [
         {
           "name": "nginx.testing-kl92-s0.marathon.mesos.",
           "ip": [
             "10.0.0.1",
             "11.0.0.1"
           ],
           "tcp": {
             "rpc":31200,
             "web":31201,
             "sip":32000
           },
           "udp": {
             "sip":31201
           }
         },
         {
           "name": "nginx.testing-kl123-s1.marathon.mesos.",
           "ip": [
             "10.0.0.2",
             "11.0.0.2"
           ],
           "tcp": {
             "rpc":31210,
             "web":31211,
             "sip":32010
           },
           "udp": {
             "sip":31211
           }
         }
      ],
     "email": [
         {
           "name": "nginx.testing-kl92-s0.marathon.mesos.",
           "ip": [
             "10.0.0.1"
           ],
           "tcp": {
             "smtp":31200,
             "pop":31201
           }
         }
      ],
     "anyport": [
         {
           "name": "nginx.testing-kl92-s0.marathon.mesos.",
           "ip": [
             "10.0.0.1"
           ],
           "tcp": [
             31200,
             31201
           ]
         }
      ]
   "env": {
      "HOME": "/var/lib/nginx"
   }
}
```

#### Real template example

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

#### Checks in template

_my['env']_ is a python os.environ class. Look bellow:
```
{% if my['env'].get('DB_HOST') %}
host = '{{my['env']['DB_HOST']}}'
{% else %}
host = 'localhost'
{% endif %}
```

### 0.7 version 

my dictionary in template
```
{
   "services": {
     "nginx": [
         {
          "name": "nginx.testing-kl92-s0.marathon.mesos.",
          "port": "31200"
         },
         {
          "name": "nginx.testing-kl123-s1.marathon.mesos.",
          "port": "32230"
         }
      ],
      "emailsender": [
         {
          "name": "emailsender.testing-kl92-s0.marathon.mesos.",
          "port": "31201"
         },
         {
          "name": "emailsender.testing-kl123-s1.marathon.mesos.",
          "port": "32232"
         }
      ],
     "service-with-defined-ports": {
         "name-of-port0": [
           {
             "name": "f.q.d.n",
             "port": 12341
           }
         ],
         "name-of-port2": [
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

#### Real template example

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
