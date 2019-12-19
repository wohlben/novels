#!/bin/bash

# development script to run all relevant daemons locally

function webpack(){
	nohup bash -c 'gnome-terminal -- bash -c "cd ~/code/novels/src/assets && npx webpack --mode development --watch"'
}

function celery() {
	nohup bash -c 'gnome-terminal -- bash -c "cd ~/code/novels/src && poetry run celery -A app worker  -E -l info -B"' & > /dev/null 2>&1
}


function django() {
	nohup bash -c 'gnome-terminal -- bash -c "cd ~/code/novels/src && poetry run python manage.py runserver 0.0.0.0:8000"' & > /dev/null 2>&1
}

function shell(){
	st -- bash --rcfile <(echo ". ~/.bashrc ; . ~/code/novels/.venv/bin/activate; cd ~/code/novels/src; ls --color")
}

if [[ $# -ne 0 ]]; then
	$@
else
	webpack
	sleep 0.2
	celery
	sleep 0.2
	django
	sleep 0.2
	shell
fi
