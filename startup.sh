

wait-for-it cache:6379 -t 30
wait-for-it database:5432 -t 30

variant=$1
if [[ $variant == "celery" ]]; then
  celery -A app worker  -E -l info -B || echo "sleeping a while in case django is still migrating"
  sleep 10
  celery -A app worker  -E -l info -B
fi
if [[ $variant == "django" ]]; then
  python manage.py migrate
  python manage.py runserver
fi

echo "please choose a valid variant"
exit 2
