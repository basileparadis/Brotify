#!/bin/sh
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
celery -A Brotify worker -l info -D
exec "$@"