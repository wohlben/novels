#!/usr/bin/env bash
set -eux

function migrations(){
  pipenv run python manage.py migrate
  pipenv run python /open_port.py
}

function celery-worker(){
  pipenv run celery -A app worker -E -l info -B
}

function django(){
  pipenv run gunicorn app.wsgi --access-logfile=- --log-level=${LOG_LEVEL:-info} --workers=${WORKERS:-3} --bind 0.0.0.0:8000
}

function help(){
  echo "please choose a valid variant"
  exit 2
}

${variant}
