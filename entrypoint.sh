#!/usr/bin/env bash

# Start cron
sudo service cron start

# Default to dev
[[ -z $SCOVID_ENV ]] && SCOVID_ENV='dev'

# Create user cron if it doesn't exist
# NOTE: This exits with a non zero
crontab -l >/dev/null 2>&1

# Add to cron
cat << EOF | crontab -
PATH="$PATH:/usr/local/bin"

# Download new data every dat at 2pm
0 14 * * * bash -c 'cd $SCOVID_PROJECT_ROOT && python3 $SCOVID_PROJECT_ROOT/tools/update_db.py'

# Post tweet every day at 3pm
0 15 * * * bash -c 'cd $SCOVID_PROJECT_ROOT && python3 -m app.scripts.tweet'
EOF

# Create db if it doesn't exist
if [[ ! -f $DATABASE ]]; then
    ./tools/update_db.py
fi

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
        'app:create_app()'
fi
