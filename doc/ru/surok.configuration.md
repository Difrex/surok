# Конфигурация Surok

**/etc/surok/conf/surok.json**
Разберем конфигурационный файл по опциям
```
{
    "marathon": "10.0.1.199:8080",
    "confd": "/etc/surok/conf.d",
    "domain": "marathon.mesos",
    "wait_time": 20,
    "lock_dir": "/var/tmp",
    "loglevel": "info|debug"
    "container": true|false
}
```

* marathon(v0.7) - string. Адрес Marathon Sheduler.
* confd - strig. Абсолютный путь до директории с конфигурационными файлами приложений.
* domain - string. Домен, который обслуживает mesos-dns.
* wait_time - int. Время в секундах сколько Surok ждет до того, как начать заново делать запросы на обнаружение сервисов.
* lock_dir - string. Абсолютный путь до директории с lock-конфигурациями.
* loglevel - string. Уровень логирования.
* container(v0.6) - boolean. Определяем внутри или нет контейнера запущен сурок. Меняется логика работы.
