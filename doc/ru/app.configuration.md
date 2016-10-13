# Конфигурация приложения

/etc/surok/conf.d/app.json
```
{
    "services": [
      {
        "name": "kioskservice",
        "group": "production.romania",
        "ports": ["web", "socket"]
      }
    ],
    "conf_name": "kiosk",
    "template": "/etc/surok/templates/kiosk.jj2",
    "dest": "/etc/nginx/sites-available/kioskservice.conf",
    "reload_cmd": "/bin/systemctl reload nginx",
    "run_cmd": ["/usr/bin/node", "-c", "config.json"]
}
```

Давайте разберем конфигурационный файл по опциям
* services - array. Список хэшей с описанием сервисов
    name - string. Имя сервиса. Это имя приложения в marathon
    group - string. Группа в которой находится сервис. Группу можно узнать в marathon. Записывается в обратном порядке. Т.е. если у нас есть группа /webapps/php, то записывать её следует, как php.webapps
    Если группа не указана, то сурок ожидает группу в переменной окружения SUROK_DISCOVERY_GROUP, если и SUROK_DISCOVERY_GROUP нет, то берется группа marathon(0.5.5).
    ports - array.  Список имен портов сервиса. Не обязательная опция.
* conf_name - string. Название конфига. Должен быть уникальным значением. Слежит для создания и чтения lock конфигурации.
* template - string. Абсолютный путь к файлу шаблона.
* dest - string. Абсолютный путь к файлу в который запишется результат генерации шаблона.
* reload_cmd - string. Команда, которая будет выполнена в случае обноления конфига.
    В reload_cmd можно использовать переменные окружения:
    ```"reload_cmd": "/usr/bin/killall -9 calc || true && /usr/local/bin/calc -c /app/calc.conf ${CALC_NUM}"```
* run_cmd(v0.6) - array. Список с командой на выполнение. Используется внутри контейнера вместо reload_cmd.
