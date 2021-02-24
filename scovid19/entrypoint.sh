#!/usr/bin/env bash

# Start cron
sudo service cron start
(crontab -l 2>/dev/null; echo "0 15 * * * bash -c 'cd $PROJECT_ROOT && /usr/local/bin/python3 -m scovid19.scripts.scraper'") | crontab -
(crontab -l 2>/dev/null; echo "5 15 * * * bash -c 'cd $PROJECT_ROOT && /usr/local/bin/python3 -m scovid19.scripts.tweet'") | crontab -

# Start web server
./control.sh --env $ENV --flask up --in-container
