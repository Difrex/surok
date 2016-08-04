#!/bin/bash

echo "invoke reload ${APP_NAME} `date`"

APP_PATH='/app'
APP_RUN='node app.js -c /app/conf.json'
APP_MASTER_NAME='node'


function run_reload() {
    (
        cd $APP_PATH
        echo "$$" > /tmp/spid${APP_NAME}
        $APP_RUN
    )&
}


if [[ -e /tmp/spid${APP_NAME} ]]; then
    SPID=`cat /tmp/spid${APP_NAME}`
fi

if [[ -z $SPID ]]; then
    run_reload
else
    killall -9 $APP_MASTER_NAME
    run_reload
fi
