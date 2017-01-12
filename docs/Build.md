# Build packages and images

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

ENTRYPOINT is: ```cd /opt/surok && pytho3 surok.py -c /etc/surok/conf/surok.json```
