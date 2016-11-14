function cleanup() {
		echo 'Cleanup'
		rm -rf ./surok
		rm -rf ./out
		rm -f ./Dockerfile*
}

function copy_surok() {
		mkdir -p ./surok
		for f in ../*; do
				if [[ $f != '../.git' ]] && [[ $f != '../build' ]]; then
						cp -r $f ./surok;
				fi
		done

		SUROK_DEPS=$(grep '^Depends:' surok/debian/control | awk -F': ' '{print $2}' | sed 's/,//g')
		CUR_DIR=$(pwd)
}

function build_builder() {
		copy_surok
		cat > Dockerfile.builder <<EOF
FROM ubuntu:xenial

# Build debian package

MAINTAINER Denis Zheleztsov <difrex.punk@gmail.com>

# Install build depends
RUN apt-get update
RUN apt-get -y install devscripts debhelper
RUN apt-get clean

COPY surok /opt/surok_build

ENTRYPOINT cd /opt/surok_build && dpkg-buildpackage -uc -us && \
mv /opt/surok_*.deb /opt/out
EOF
}

function build_package() {
		# run build
		echo 'Build builder'
		docker build -t surok_builder:latest -f Dockerfile.builder .
		docker run -ti -v $CUR_DIR/out:/opt/out surok_builder:latest
}

function build_surok_base() {
		if [[ $1 == 'rebuild' ]]; then
				build_builder
				build_package
		fi

		DEB=$(cd out && ls | grep .deb)

		cat > Dockerfile.surok <<EOF
FROM ubuntu:xenial

MAINTAINER Denis Zheleztsov <difrex.punk@gmail.com>

ADD out/${DEB} /tmp
RUN apt-get update && apt-get install -y ${SUROK_DEPS} python3-memcache
RUN dpkg -i /tmp/${DEB}
RUN apt-get clean
RUN rm -rf /tmp/*

ENTRYPOINT cd /opt/surok && python3 surok.py -c /etc/surok/conf/surok.json
EOF
		docker build -t surok_base:latest -f Dockerfile.surok .
}

function build_alpine() {
		copy_surok
		cat > Dockerfile.alpine << EOF
FROM alpine:latest

MAINTAINER Denis Zheleztsov <difrex.punk@gmail.com>

# Install Python
RUN apk update && apk add python3

# Upgrade pip
RUN pip3 install --upgrade pip

RUN pip3 install dnspython
RUN pip3 install jinja2
RUN pip3 install requests
RUN pip3 install python-memcached

COPY surok /opt/surok

ENTRYPOINT cd /opt/surok && python3 surok.py -c /etc/surok/conf/surok.json
EOF
		docker build -t surok_alpine -f Dockerfile.alpine .
}

function build_centos() {
    copy_surok
    cat > Dockerfile.centos <<EOF
FROM centos:latest

MAINTAINER Denis Zheleztsov <difrex.punk@gmail.com>

RUN yum -y install epel-release
RUN yum -y install python34

# Install pip
RUN cd /tmp && curl -O https://bootstrap.pypa.io/get-pip.py
RUN cd /tmp && python3.4 get-pip.py

# Install surok
COPY surok /opt/surok
RUN mkdir /etc/surok
RUN ln -s /opt/surok/conf /etc/surok/conf
RUN ln -s /opt/surok/conf.d /etc/surok/conf.d
RUN ln -s /opt/surok/templates /etc/surok/templates

# Install surok depends
RUN cd /opt/surok && pip3 install -r requriments.txt

# Cleanup
RUN yum clean all

ENTRYPOINT cd /opt/surok && python3 surok.py -c /etc/surok/conf/surok.json
EOF
    docker build -t surok_centos -f Dockerfile.centos .
}
