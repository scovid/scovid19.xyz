#!/usr/bin/env bash

# Defaults
env='dev'

# Arg parse
while [[ "$#" -gt 0 ]]; do
	case "$1" in
		--env) env=$2; shift ;;
		--docker) docker=$2; shift ;;
		--flask) flask=$2; shift ;;
		-h|--help) help=1 ;;
		-f|--force) force=1 ;;
		--) shift; break ;;
	esac

	shift
done

# Show help on bad usage
if [[ -z $flask && -z $docker ]]; then
	echo 'Requires one of --flask or --docker'
	echo
fi

if [[ $help ]]; then
	cat << EOF
./control.sh --env <dev|prod> [--flask cmd] [--docker cmd] [--flags]

Used for running the scovid19.xyz web app.
Should be ran from the app root.

env should be either 'dev' or 'prod' (defaults to dev).

Flask
	up: Starts the flask server

Docker
	up:      Builds and starts a container, pass -f to force rebuild
	down:    Stop a container
	restart: Restart a container
	deploy:  Stops and recreates the container
EOF

	exit 0
fi

if [[ ! -d src || ! -f src/app.py ]]; then
	echo 'This script needs to be ran from the app root'
	exit 1
fi

# Dev using flask
if [[ $flask == 'up' ]]; then
	# Set up virtual env if not already done
	if [[ ! -d venv ]]; then
		python -m venv venv
		source venv/bin/activate
		pip install -r requirements.txt
	fi

	if [[ $env == 'dev' ]]; then
		source venv/bin/activate
		FLASK_APP=src/app.py FLASK_ENV=development FLASK_DEBUG=True flask run --host 0.0.0.0

	elif [[ $env == 'prod' ]]; then
		source venv/bin/activate
		gunicorn --bind 0.0.0.0:5000 --chdir src/ wsgi:app

	else
		echo "Invalid env value '$env'"
	fi

	exit 0
fi

# Docker
if [[ -n $docker ]]; then
	name='scovid'

	# Build and run
	if [[ $docker == 'up' ]]; then
        running=$(docker ps -q -f name=$name)

		if [[ $running && -z $force ]]; then
			echo "$name container is already running, pass --force to rebuild"
			exit 1
		fi

		# If prod mode then
		# - ensure we restart on failure
		# - pull the latest base image
		# - don't use the cache (https://pythonspeed.com/articles/docker-cache-insecure-images/)
		[[ $env == 'prod' ]] && extra_build='--pull --no-cache'
		[[ $env == 'prod' ]] && extra_run='--restart=unless-stopped'
		export ENV=$env

		extra=""
		if [[ -n $force ]]; then
			extra=" --build --no-deps"
		fi

		docker-compose up -d $extra
		echo "Built and started $name"

	# Stop
	elif [[ $docker == 'down' ]]; then
		docker-compose down
		echo "Container $name brought down"

	# Restart
	elif [[ $docker == 'restart' ]]; then
		docker-compose stop
		docker-compose start
		echo "Container $name restarted"

	elif [[ $docker == 'deploy' ]]; then
		# Scale up to 2 containers, the new one being our new build
		# Kill the old container, then scale down to 1
		echo "Scaling up $name (NOTE: You can ignore the following two warnings about the container name and port)"
		docker rename $name "${name}_old"
		docker-compose up -d --scale app=2 --no-recreate

		echo "Building new container"
		sleep 20

		echo "New container built, removing old one"
		docker rm -f "${name}_old"
		docker-compose up -d --scale app=1 --no-recreate
		echo "Deploy finished"

	else
		echo "Invalid docker subcommand '$sub'"
	fi

	exit 0
fi
