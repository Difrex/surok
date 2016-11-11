# Surok
[![Build Status](https://travis-ci.org/Difrex/surok.svg?branch=master)](https://travis-ci.org/Difrex/surok)

Обнаружение сервисов для Apache Mesos.

* Конфигурация на Jinja2
* Обнаружение через mesos-dns
* Перезагрузка конфигурации приложения

## Сборка

Сборка deb-пакета
```
cd build
./build.sh build_package
```
deb-пакет будет лежать в build/out

Сборка базового docker-образа surok
```
cd build
./build.sh surok_image
```

## Известные проблемы

* В Debian Jessie поломан пакет python3-memcache. Бэкпортируйте свежую версию из testing (>= 1.57).
