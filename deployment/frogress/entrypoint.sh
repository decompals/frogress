#!/usr/bin/env bash

until nc -z ${POSTGRES_HOST} ${POSTGRES_PORT} > /dev/null; do
    echo "Waiting for database to become available on ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    sleep 1
done

poetry run python manage.py migrate

poetry run gunicorn frogress.wsgi
