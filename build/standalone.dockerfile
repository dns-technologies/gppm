######################################
#    GreenPlum Permission Manager    #
#            stand alone             #
#              preview               #
######################################

###########
# BACKEND #
###########
FROM python:3.9-slim-buster as standalone
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc curl libsasl2-dev libldap2-dev \
        gnupg2 ca-certificates wget procps psmisc gosu && \
    apt-get clean
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh
WORKDIR /app
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.14 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app
RUN pip install "poetry==$POETRY_VERSION"
COPY backend/app/pyproject.toml backend/app/poetry.lock* ./
RUN poetry install --no-root --no-dev
COPY backend/app .
ENV PORT=8080 \
    BACKEND_CORS_ORIGINS='["http://localhost", "https://localhost"]' \
    PROJECT_NAME="GreenPlum Permission Manager Preview" \
    FIRST_SUPERUSER=admin@gppm.com \
    FIRST_SUPERUSER_PASSWORD=admin
EXPOSE 8080

####################
# FRONTEND BUILDER #
####################
FROM node:16.14-slim as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/. .
ENV VUE_APP_NAME="GreenPlum Permission Manager Preview" \
    VUE_APP_DOMAIN=localhost:8080
RUN npm run build

############
# FRONTEND #
############
FROM standalone as standalone-nginx
ENV NGINX_VERSION=1.20.2-1~buster
RUN wget --quiet -O - http://nginx.org/keys/nginx_signing.key | apt-key add - \
      && echo "deb http://nginx.org/packages/debian buster nginx" | tee /etc/apt/sources.list.d/nginx.list
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx=$NGINX_VERSION && \
    apt-get clean
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist/ /usr/share/nginx/html
COPY build/nginx.conf /etc/nginx/nginx.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
EXPOSE 80

#############################
# ADD POSTGRESQL TO BACKEND #
#############################
FROM standalone-nginx as standalone-postgresql
ENV PG_VERSION=9.6 \
    PG_BASE=/var/lib/postgresql
ENV PG_PASSWORD_FILE=${PG_BASE}/pwfile \
    PG_DATA=${PG_BASE}/${PG_VERSION}/main \
    PG_CONFIG_DIR=/etc/postgresql/${PG_VERSION}/main
ENV PG_CONFIG_FILE=${PG_CONFIG_DIR}/postgresql.conf \
    PG_BINDIR=/usr/lib/postgresql/${PG_VERSION}/bin
ENV POSTGRES_SERVER=localhost \
    POSTGRES_PORT=5432 \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=changethis \
    POSTGRES_DB=app
ENV PATH="${PATH}:${PG_BINDIR}"
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
      && echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" | tee /etc/apt/sources.list.d/postgresql-pgdg.list
RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           postgresql-$PG_VERSION \
           postgresql-client-$PG_VERSION \
           postgresql-contrib-$PG_VERSION \
      && apt-get clean
RUN rm -rf "$PG_BASE" && mkdir -p "$PG_BASE" && chown -R postgres:postgres "$PG_BASE" \
      && mkdir -p /var/run/postgresql/$PG_VERSION-main.pg_stat_tmp \
      && chown -R postgres:postgres /var/run/postgresql && chmod g+s /var/run/postgresql
RUN echo "host all  all    0.0.0.0/0  md5" >> $PG_CONFIG_DIR/pg_hba.conf \
      && echo "host all  all    ::/0  md5" >> $PG_CONFIG_DIR/pg_hba.conf \
      && echo "listen_addresses='*'" >> $PG_CONFIG_FILE
EXPOSE 5432

############################
# ADD ENTRYPOIN TO BACKEND #
############################
FROM standalone-postgresql
LABEL maintainer="Ostap Konstantinov <konstantinov.ov@dns-shop.ru>"
COPY build/postgres.sh /postgres.sh
RUN chmod +x /postgres.sh
COPY build/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
STOPSIGNAL SIGINT
CMD ["/docker-entrypoint.sh"]
