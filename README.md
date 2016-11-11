# Surok

Service discovery for Apache Mesos.

* Jinja2 Templates
* Discovery over mesos-dns
* Applications config reload

## Build

build debian package
```
cd build
./build.sh build_package
```
A deb-package will be placed in build/out

build surok base docker image
```
cd build
./build.sh surok_image
```

## Known issues

* python3-memcache is broken in Debian Jessie. Backport fresh version from testing (>= 1.57).
