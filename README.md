# Surok

Обнаружение сервисов для Apache Mesos.

* Конфигурация на Jinja2
* Обнаружение через mesos-dns
* Перезагрузка конфигурации приложения

## Сборка

Сборка deb-пакета
```
cd build
./build build_package
```
deb-пакет будет лежать в build/out

Сборка базового docker-образа surok
```
cd build
./build surok_image
```
