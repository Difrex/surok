# Surok
[![Build Status](https://travis-ci.org/Surkoveds/surok.svg?branch=master)](https://travis-ci.org/Surkoveds/surok)

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
Ubuntu Xenial
```
cd build
./build.sh surok_image
```
Alpine image
```
cd build
./build.sh alpine
```
CentOS image
```
cd build
./build.sh centos
```

ENTRYPOINT : ```cd /opt/surok && pytho3 surok.py -c /etc/surok/conf/surok.json```

## Документация

[Wiki](https://github.com/Surkoveds/surok/wiki)

## Известные проблемы

* В Debian Jessie поломан пакет python3-memcache. Бэкпортируйте свежую версию из testing (>= 1.58).
