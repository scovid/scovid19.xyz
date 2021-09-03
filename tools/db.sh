#!/usr/bin/env bash

# Lazy script to connect to start an sqlite3 shell in the container
docker exec -it scovid sqlite3 data/scovid19.db
