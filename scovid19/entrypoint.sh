#!/usr/bin/env bash

# Start cron
sudo service cron start

# Default to dev
[[ -z $SCOVID_ENV ]] && SCOVID_ENV='dev'

# Create our env file
printenv | grep -e '^SCOVID_' > "$SCOVID_PROJECT_ROOT/.env"

# Create user cron if it doesn't exist
# NOTE: This exits with a non zero
crontab -l >/dev/null 2>&1

# Add to cron
# Every day at 15:00 run the scraper and tweet results
cat << EOF | crontab -
PATH="$PATH:/usr/local/bin"
0 15 * * * bash -c 'cd $SCOVID_PROJECT_ROOT && python3 -m scovid19.scripts.tweet'
EOF

# Start web server
./control.sh --env $SCOVID_ENV --flask up --in-container
