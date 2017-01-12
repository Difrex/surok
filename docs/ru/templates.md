# Шаблоны

Шаблоны для Surok пишутся на Jinja2. Возможно, стоит прочитать документацию.

## Словарь my в шаблоне

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

