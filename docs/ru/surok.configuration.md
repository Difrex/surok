# Конфигурация Surok (0.7.x)

**/etc/surok/conf/surok.json**
Разберем конфигурационный файл по опциям
```
{
    "marathon": {
	"force": true,
	"host": "marathon.mesos:8080",
	"enabled": true
    },
    "confd": "/etc/surok/conf.d",
    "domain": "marathon.mesos",
    "wait_time": 20,
    "lock_dir": "/var/tmp",
    "loglevel": "info|debug"
    "container": true|false
}
```

* marathon(v0.7) - hash. В текущей версии отвечает за перезапуск контейнера. Обнаружение сервисов через Marathon пока недоступно.
  1. force - boolean. Рестарт контейнера с force или нет.
  2. host - string. Адрес Marathon.
  3. enabled - boolean. Вкл/выкл.
* confd - strig. Абсолютный путь до директории с конфигурационными файлами приложений.
* domain - string. Домен, который обслуживает mesos-dns.
* wait_time - int. Время в секундах сколько Surok ждет до того, как начать заново делать запросы на обнаружение сервисов.
* lock_dir - string. Абсолютный путь до директории с lock-конфигурациями.
* loglevel - string. Уровень логирования.
* container(v0.6) - boolean. Определяем внутри или нет контейнера запущен сурок. Меняется логика работы.
