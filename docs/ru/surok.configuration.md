# Конфигурация Surok (0.8.x)
**/etc/surok/conf/surok.json** Разберем конфигурационный файл по опциям
```
{
    "version": "0.8"
    "marathon": {
        "enabled": false,
        "restart": false,
        "force": true,
        "host": "http://marathon.mesos:8080"
    },
    "default_discovery": "mesos_dns",
    "confd": "/etc/surok/conf.d",
    "wait_time": 20,
    "lock_dir": "/var/tmp",
    "loglevel": "info",
    "memcached": {
        "enabled": false,
        "discovery": {
            "enabled": false,
            "service": "memcached",
            "group": "system"
        },
        "hosts": ["localhost:11211"]
    }
}
```
## Опции файла конфигурации
* **version** - *string. Не обязательный. По умолчанию "0.7".*
Версия файлов конфигурации, шаблонов. На текущий момент может принимать значения "0.7" или "0.8".
  * значение "0.7" - файлы конфигурации версии 0.7.х и более ранних
  * значение "0.8" - файлы конфигурации версии 0.8

##### версия 0.8
* **marathon**, **mesos**, **consul**, **memcached** - *dict/hash. Не обязательный. По умолчанию '{"enable":false}'.*
Системы с которыми работает сурок. Если система выключена, то параметры системы и их наличие уже не важны.
  * **enable** - *boolean. Не обязательный. По умолчанию false.*
    Доступность системы для использования.

    специфичные параметры:
    * для Marathon API "marathon"
      * **force** - *boolean. Не обязательный. По умолчанию true.*
        Рестарт контейнера с force или нет.
      * **restart** - *boolean. Не обязательный. По умолчанию false.*
        Вкл/выкл. рестарта контейнера
      * **host** - *string. Не обязательный. По умолчанию "http://marathon.mesos:8080".*
        Адрес Marathon.
    * для mesos DNS "mesos"
      * **domain** - *string. Не обязательный. По умолчанию "marathon.mesos".*
        Приватный домен Mesos DNS
    * для Memcached "memcached"
      * **hosts** - 
      * **discovery** - 
        * **enabled** - 
        * **service** - 
        * **group** - 
* **default_discovery** - *string. Не обязательный. По умолчанию "mesos_dns".*

  Может принимать значения:
  * "mesos_dns" - Mesos DNS
  * "marathon_api"- Marathon API
* **confd** - *strig. Обязательный.*
  Абсолютный путь до директории с конфигурационными файлами приложений.
* **wait_time** - *int. Обязательный.*
  Время в секундах сколько Surok ждет до того, как начать заново делать запросы на обнаружение сервисов.
* **lock_dir** - *string. Обязательный.*
  Абсолютный путь до директории с lock-конфигурациями.
* **loglevel** - *string. Не обязательный. По умолчанию "info".*
  Уровень логирования. Может принимать значения: "debug", "info", "warning", "error"

##### версия 0.7 и более ранние
Особенности для файла конфигурации
* **marathon**
  * **enabled** - boolean. Вкл/выкл. рестарта контейнера. В версии 0.8 переименована в "restart".
* **domain** - string. Приватный домен Mesos DNS. В версии 0.8 перемещен в dict "mesos".
  Обнаружение Mesos DNS включено всегда.

