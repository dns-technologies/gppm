#!/bin/sh

if [ ! -d "${PG_DATA}" ]; then
    echo "${POSTGRES_PASSWORD}" > ${PG_PASSWORD_FILE}
    initdb \
        --pgdata=${PG_DATA} \
        --pwfile=${PG_PASSWORD_FILE} \
        --username=${POSTGRES_USER} \
        --encoding=UTF8 \
        --auth=trust
fi

pg_ctl -D ${PG_DATA} \
    -o "-c config_file=${PG_CONFIG_FILE}" \
    -w start

psql -c "CREATE DATABASE ${POSTGRES_DB};" 2> /dev/null

exit 0
