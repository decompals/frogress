#!/usr/bin/env bash

until nc -z ${DATABASE_HOST} ${DATABASE_PORT} > /dev/null; do
    echo "Waiting for database to become available on ${DATABASE_HOST}:${DATABASE_PORT}..."
    sleep 1
done

poetry run python manage.py migrate

poetry run gunicorn frogress.wsgi
