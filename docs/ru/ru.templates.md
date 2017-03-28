# Шаблоны

Шаблоны для Surok пишутся на Jinja2. Возможно, стоит прочитать документацию.

## Словарь my в шаблоне

### Версия 0.8
Surok заполняет словарь my и передает его в шаблон.
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

## Пример реального шаблона

```
upstream matrix-http {
    hash $remote_addr;
{% for server in my['services']['matrix'] %}
    server {{server['name']}}:{{server['tcp']['http']}} max_fails=3;
{% endfor %}
}

upstream riot-http {
    hash $remote_addr;
{% for server in my['services']['riot'] %}
    server {{server['name']}}:{{server['tcp'][0]}} max_fails=3;
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
Так для upstream matrix-http используются именованные порты, а для riot-http – нет.

## Проверки в шаблоне

Переменная _my['env']_ является классом python _os.environ_, что позваоляет нам строить различные проверки, например:

```
{% if my['env'].get('DB_HOST') -%}
host = '{{my['env']['DB_HOST']}}'
{% else -%}
host = 'localhost'
{% endif -%}
```

### Версия 0.7
Surok заполняет словарь my и передает его в шаблон.
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

## Пример реального шаблона

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
Так для upstream matrix-http используются именованные порты, а для riot-http – нет.

## Проверки в шаблоне

Переменная _my['env']_ является классом python _os.environ_, что позваоляет нам строить различные проверки, например:

```
{% if my['env'].get('DB_HOST') %}
host = '{{my['env']['DB_HOST']}}'
{% else %}
host = 'localhost'
{% endif %}
```

