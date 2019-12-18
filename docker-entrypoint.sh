#!/bin/bash

while ! nc -z ${RMQ_HOST} ${RMQ_PORT}; do sleep 3; done

celery worker\
  --app=verify.worker.app\
  --queues=${VERIFY_Q}\
  --concurrency=${CONCURRENCY}\
  --loglevel=${LOG_LEVEL}\
  --without-mingle\
  --without-gossip
