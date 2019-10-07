FROM python:3.7-slim AS base

ENV LOG_LEVEL info

FROM base AS builder

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

ADD . /app

CMD ["celery", "worker", "--app=tardis.celery.app", "--queues=verify", "--loglevel=${LOG_LEVEL}"]

FROM builder AS test

RUN pip3 install --no-cache-dir -r requirements-test.txt

RUN mkdir /var/store

# This will keep container running...
CMD ["tail", "-f", "/dev/null"]
