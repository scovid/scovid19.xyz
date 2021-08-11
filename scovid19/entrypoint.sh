#!/usr/bin/env bash

# Start cron
sudo service cron start

# Default to dev
[[ -z $SCOVID_ENV ]] && SCOVID_ENV='dev'

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
if [[ $SCOVID_ENV == 'dev' || $SCOVID_ENV == 'development' ]]; then
    exec flask run --host 0.0.0.0
else
    exec gunicorn \
        --workers 4 \
        --threads 4 \
        --worker-class gevent \
        --bind 0.0.0.0:5000 \
        --worker-tmp-dir /dev/shm \
        --log-level debug \
        --capture-output \
        --enable-stdio-inheritance \
        scovid19:app
fi
