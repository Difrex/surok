# Surok
[![Build Status](https://travis-ci.org/Difrex/surok.svg?branch=master)](https://travis-ci.org/Difrex/surok)

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

build surok base docker image(based on Ubuntu Xenial)
```
cd build
./build.sh surok_image
```

build surok base Alpine image
```
cd build
./build.sh alpine
```

build surok base CentOS image
```
cd build
./build.sh centos
```

## Documentation

[Wiki](https://github.com/Difrex/surok/wiki)

## Known issues

* python3-memcache is broken in Debian Jessie. Backport fresh version from testing (>= 1.57).
