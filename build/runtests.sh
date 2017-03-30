#!/bin/bash

set -e

. functions.sh

function run_tests() {
        [ -z "$(docker ps -q -f name=surok-memcache)" ] && \
        docker run -d --name surok-memcache memcached
        docker run --rm -ti \
                     --link surok-memcache:memcache \
                     -v $(pwd)/tests.py:/opt/surok/tests.py \
                     -v $(pwd)/tests_entrypoint.sh:/tests_entrypoint.sh \
                     --entrypoint /tests_entrypoint.sh \
                     surok_base:latest
}

run_tests && docker stop -t0 surok-memcache && docker rm -f surok-memcache || \
	OE=$?; docker stop -t0 surok-memcache && docker rm -f surok-memcache && exit $OE
