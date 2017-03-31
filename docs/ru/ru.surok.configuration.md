# Конфигурация Surok (0.8.x)
**/etc/surok/conf/surok.json** Разберем конфигурационный файл по опциям
```
{
    "version": "0.8",
    "marathon": {
        "enabled": false,
        "restart": false,
        "force": true,
        "host": "http://marathon.mesos:8080"
    },
    "mesos":{
        "enabled": true,
        "domain": "marathon.mesos"
    },
    "default_discovery": "mesos_dns",
    "default_store": "memory",
    "confd": "/etc/surok/conf.d",
    "modules": "/opt/surok/modules",
    "wait_time": 20,
    "files":{
        "enabled": false,
        "path": "/var/tmp"
    },
    "loglevel": "info",
    "memcached": {
        "enabled": false,
        "discovery": {
            "enabled": false,
            "service": "memcached",
            "group": "system"
        },
        "host": "localhost:11211"
    }
}
```
## Опции файла конфигурации
* **version** - *string. Не обязательный. По умолчанию "0.7".*
Версия файлов конфигурации, шаблонов. На текущий момент может принимать значения "0.7" или "0.8".
  * значение "0.7" - файлы конфигурации версии 0.7.х и более ранних
  * значение "0.8" - файлы конфигурации версии 0.8

##### версия 0.8
* **marathon**, **mesos**, **memcached**, **files** - *dict/hash. Не обязательный. По умолчанию '{"enable":false}'.*
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
      * **host** - string. Адрес Memcached сервера в формате, "FQDN:порт" или "IP-адрес:порт"
                   В случае отсутствия обнаруженных хостов через обнаружение, используется как "резерв".
      * **discovery** - Параметры обнаружения Memcached в Mesos
        * **enabled** - *boolean. Не обязательный. По умолчанию false.*
           Вкл/выкл. обнаружение
        * **service** - *string. Обязательный, если обнаружение включено."
           Имя сервиса в Mesos
        * **group** - *string. Обязательный, если обнаружение включено."
           Имя группы в Mesos
    * для файлового хранилища "files"
      * **path** - *string. Абсолютный путь к хранилищу.*

* **default_discovery** - *string. Не обязательный. По умолчанию "mesos_dns".*

  Может принимать значения:
  * "mesos_dns" - Mesos DNS
  * "marathon_api"- Marathon API
* **default_store** - *string. Не обязательный. По умолчанию "memory".*

  Может принимать значения:
  * "memory" - Оперативная память в рамках процесса Surok
  * "files"- Файловое хранилище
  * "memcached"- Memcached
* **confd** - *strig. Не обязательный. По умолчанию "/etc/surok/conf.d"*
  Абсолютный путь до директории с конфигурационными файлами приложений.
* **modules** - *strig. Не обязательный. По умолчанию "/opt/surok/modules"*
  Абсолютный путь до директории с модулями.
* **wait_time** - *int. Не обязательный. По умолчению 20*
  Время в секундах сколько Surok ждет до того, как начать заново делать запросы на обнаружение сервисов.
* **loglevel** - *string. Не обязательный. По умолчанию "info".*
  Уровень логирования. Может принимать значения: "debug", "info", "warning", "error"

##### версия 0.7 и более ранние
Особенности для файла конфигурации
* **marathon**
  * **enabled** - boolean. Вкл/выкл. рестарта контейнера. В версии 0.8 переименована в "restart".
* **domain** - string. Приватный домен Mesos DNS. В версии 0.8 перемещен в dict "mesos".
  Обнаружение Mesos DNS включено всегда.
* **lock_dir** - string. Абсолютный путь до директории с файловым хранилищем.
  В версии 0.8 перемещен в dict "files", параметр "path".
* **mamcached**
  * **hosts** - string. Адрес Memcached сервера в формате, ["FQDN:порт"] или ["IP-адрес:порт"]
