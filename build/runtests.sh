#!/bin/bash

set -e

. functions.sh

function run_tests() {
		docker run --rm -ti -v $(pwd)/tests.py:/opt/surok/tests.py \
					 -v $(pwd)/tests_entrypoint.sh:/tests_entrypoint.sh \
					 --entrypoint /tests_entrypoint.sh \
					 surok_base:latest
}

run_tests
