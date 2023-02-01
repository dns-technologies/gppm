#!/bin/sh

set -e

run_nginx() {
    nginx
}

run_backend() {
    /start-reload.sh &
}

run_postgres() {
    chown -R postgres:postgres "${PG_BASE}"
    gosu postgres /postgres.sh
}

shutdown() {
    trap '' INT TERM EXIT
    echo "\n### GRACEFUL. Clean ($1) up and Exit ###\n"
    nginx -s stop
    pkill -TERM python
    gosu postgres pg_ctl -D ${PG_DATA} \
        -o "-c config_file=${PG_CONFIG_FILE}" \
        -w stop
    sleep 1
    exit 0
}

trap 'shutdown INT' INT
trap 'shutdown TERM' TERM
trap 'shutdown EXIT' EXIT

run_postgres
run_backend
run_nginx

sleep infinity
