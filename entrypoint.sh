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
# Set the environment
$(env)

# Download new data every dat at 2pm
0 14 * * * bash -c 'cd $SCOVID_PROJECT_ROOT && python3 ./tools/update_db.py' > /tmp/update_db.log 2>&1

# Post tweet every day at 3pm
0 15 * * * bash -c 'cd $SCOVID_PROJECT_ROOT && python3 -m app.scripts.tweet' > /tmp/tweet.log 2>&1
EOF

# Create db if it doesn't exist
if [[ ! -f $DATABASE ]]; then
    echo "Generating database..."
    ./tools/update_db.py
    echo "Successfully generated database"
fi

# Start web server
if [[ $SCOVID_ENV == 'dev' || $SCOVID_ENV == 'development' ]]; then
    echo "Starting flask dev server..."
    exec poetry run flask run --host 0.0.0.0
else
    echo "Starting gunicorn server..."
    exec poetry run gunicorn \
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
