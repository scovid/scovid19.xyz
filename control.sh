#!/usr/bin/env bash

command=$1
[[ -z $command ]] && command='dev'

if [[ $command == 'help' ]]; then
	cat << EOF
./control.sh <command> [subcommand] [flags]

Used for running the scovid19.xyz web app.
Should be ran from the app root.

Commands
	dev:    Starts the dev flask server
	prod:   Starts the prod gunicorn server
	docker: Manages docker container, see below

Docker
	up:      Builds and starts a container, pass -f to force rebuild
	down:    Stop a container
	restart: Restart a container
EOF

	exit 0
fi

if [[ ! -d src || ! -f src/app.py ]]; then
	echo 'This script needs to be ran from the app root'
	exit 1
fi

# Dev using flask
if [[ $command == 'dev' ]]; then
	source venv/bin/activate
	FLASK_APP=src/app.py FLASK_ENV=development flask run
	exit 0
fi

# Prod using gunicorn
if [[ $command == 'prod' ]]; then
	source venv/bin/activate
	gunicorn --bind 0.0.0.0:5000 --chdir src/ wsgi:app
	exit 0
fi

# Docker
if [[ $command == 'docker' ]]; then
	# Wrapper function that uses Podman if Docker isn't installed
	function docker() {
		if [[ $(type -P podman) && ! $(type -P docker) ]]; then
			sudo podman "$@"
		else
			sudo docker "$@"
		fi
	}

	sub=$2
	name='scovid-container'

	# Build and run
	if [[ $sub == 'up' ]]; then
		# Delete and recreate
		if [[ -n $3 && $3 == '-f' ]]; then
			docker rm -f $name
			echo "-f flag passed, deleting any existing container"
		fi

		exists=$(docker ps -q -a -f name=$name)
		running=$(docker ps -q -f name=$name)

		if [[ $exists && $running ]]; then
			echo 'Container already running'
		elif [[ $exists ]]; then
			docker start $name
			echo "Started $name"
		else
			docker build -t vm_docker_scovid .
			docker run -d --name $name -p 5000:5000 vm_docker_scovid
			echo "Built and started $name"
		fi

	# Stop
	elif [[ $sub == 'down' ]]; then
		docker stop $name
		echo "Container $name stopped"

	# Restart
	elif [[ $sub == 'restart' ]]; then
		docker restart $name
		echo "Container $name restarted"

	else
		echo "Invalid docker subcommand '$sub'"
	fi

	exit 0
fi

echo "Invalid command '$command'"
