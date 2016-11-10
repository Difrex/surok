#!/bin/bash

set -e

function cleanup() {
		echo 'Cleanup'
		rm -rf ./surok
		rm -rf ./out
		rm -f ./Dockerfile*
}

function build_builder() {
		mkdir -p ./surok
		for f in ../*; do
				if [[ $f != '../.git' ]] && [[ $f != '../build' ]]; then
						cp -r $f ./surok;
				fi
		done

		SUROK_DEPS=$(grep '^Depends:' surok/debian/control | awk -F': ' '{print $2}' | sed 's/,//g')
		CUR_DIR=$(pwd)

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
RUN apt-get update && apt-get install -y ${SUROK_DEPS}
RUN dpkg -i /tmp/${DEB}
RUN apt-get clean
RUN rm -rf /tmp/*

ENTRYPOINT cd /opt/surok && python3 surok.py -c /etc/surok/conf/surok.json
EOF
		docker build -t surok_base:latest -f Dockerfile.surok .
}

function usage() {
		echo "$0 <clean|build_package|surok_image>"
}

case $1 in
		clean) cleanup ;;
		build_package)
				build_builder
				build_package
				;;
		build_deb) build_package ;;
		surok_image) build_surok_base	rebuild ;;
		surok_image_no_rebuild) build_surok_base ;;
		*) usage ;;
esac
