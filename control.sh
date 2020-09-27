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
EOF

	exit 0
fi

if [[ ! -d src || ! -f src/app.py ]]; then
	echo 'This script needs to be ran from the app root'
	exit 1
fi

# Dev using flask
if [[ $flask == 'up' ]]; then

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
	# Wrapper function that uses Podman if Docker isn't installed
	function dockman() {
		if [[ $(type -P podman) && ! $(type -P docker) ]]; then
			sudo podman "$@"
		else
			sudo docker "$@"
		fi
	}

	name='scovid-container'

	# Build and run
	if [[ $docker == 'up' ]]; then
		exists=$(dockman ps -q -a -f name=$name)
		running=$(dockman ps -q -f name=$name)

		# Delete and recreate
		if [[ -n $force ]]; then
			if [[ $exists ]]; then
				echo "-f flag passed, deleting existing container"
				dockman rm -f $name
			fi

			unset exists
			unset running
		fi

		if [[ $exists && $running ]]; then
			echo 'Container already running'

		elif [[ $exists ]]; then
			dockman start $name
			echo "Started $name"

		else
			extra=''

			# If prod mode then
			# - ensure we restart on failure
			# - pull the latest base image
			# - don't use the cache (https://pythonspeed.com/articles/docker-cache-insecure-images/)
			[[ $env == 'prod' ]] && extra='--restart=unless-stopped --pull --no-cache'

			echo "dockman build --build-arg env=$env -t vm_docker_scovid ."
			dockman build --build-arg env=$env -t vm_docker_scovid .
			dockman run $extra -d --name $name -p 5000:5000 vm_docker_scovid
			echo "Built and started $name"
		fi

	# Stop
	elif [[ $docker == 'down' ]]; then
		dockman stop $name
		echo "Container $name stopped"

	# Restart
	elif [[ $docker == 'restart' ]]; then
		dockman restart $name
		echo "Container $name restarted"

	else
		echo "Invalid docker subcommand '$sub'"
	fi

	exit 0
fi
