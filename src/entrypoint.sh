#!/usr/bin/env bash

# Start cron
sudo service cron start
(crontab -l 2>/dev/null; echo "0 15 * * * /usr/bin/env python3 /home/code/scovid19/src/scripts/scraper.py") | crontab -

# Start web server
./control.sh --env $ENV --flask up
