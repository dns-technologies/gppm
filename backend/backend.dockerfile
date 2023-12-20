FROM python:3.9-slim-buster

LABEL maintainer="Ostap Konstantinov <konstantinov.ov@dns-shop.ru>"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc curl procps libsasl2-dev libldap2-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.15 \
  POETRY_VIRTUALENVS_CREATE=false \
  PYTHONPATH=/app

ENV MAX_WORKERS=4

RUN pip install "poetry==$POETRY_VERSION"

COPY ./app/pyproject.toml ./app/poetry.lock* ./

RUN poetry install --no-root --no-dev

COPY ./app .

EXPOSE 80

CMD ["/start.sh"]
