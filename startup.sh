#!/usr/bin/env bash

wait-for-it cache:6379 -t 30
wait-for-it database:5432 -t 30

variant=$1
if [[ $variant == "celery" ]]; then
  sleep 10
  celery -A app worker -E -l info -B
fi
if [[ $variant == "django" ]]; then
  python manage.py migrate
  python manage.py runserver
fi

echo "please choose a valid variant"
exit 2
