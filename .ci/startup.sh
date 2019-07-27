#!/usr/bin/env bash
function migrations(){
  wait-for-it database:5432 -t 30
  poetry run python manage.py migrate
  poetry run python /open_port.py
}

function celery-worker(){
  if ${MIGRATIONS:-false}; then
    wait-for-it migrations:9999 -t 30
  fi
  wait-for-it migrations:9999 -t 30
  wait-for-it cache:6379 -t 30
  poetry run celery -A app worker -E -l info -B
}

function django(){
  if ${MIGRATIONS:-false}; then
    wait-for-it migrations:9999 -t 30
  fi
  wait-for-it database:5432 -t 30
  wait-for-it cache:6379 -t 30
  poetry run gunicorn app.wsgi:application --access-logfile=- --log-level=${LOG_LEVEL:-info} --workers=${WORKERS:-3} --name novels --bind 0.0.0.0:8000
}

function help(){
  echo "please choose a valid variant"
  exit 2
}

${variant} || help
