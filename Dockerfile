FROM python:3.7-slim AS base

ENV C_FORCE_ROOT 1
ENV LOG_LEVEL info
ENV CONCURRENCY 1

ENV VERIFY_Q verify

ENV RMQ_HOST rabbitmq
ENV RMQ_PORT 5672

RUN apt-get update && apt-get -y install netcat && apt-get clean
RUN pip install -U pip

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

ADD . /app

COPY docker-entrypoint.sh /
RUN ["chmod", "+x", "/docker-entrypoint.sh"]
ENTRYPOINT ["/docker-entrypoint.sh"]

FROM base AS test

RUN pip install --no-cache-dir -r requirements-test.txt

RUN mkdir /var/store
COPY verify/tests/assets /var/store
