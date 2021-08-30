#!/usr/bin/env python3

"""
This script will download all of the configured datasets and load them into an sqlite3 file database
"""

import sqlite3
import json
import os

database = 'data/scovid19.db'

datasets = {
    # Misc
    "population_by_council": 'https://www.opendata.nhs.scot/datastore/dump/09ebfefb-33f4-4f6a-8312-2d14e2b02ace?format=json',
    "councils": 'https://www.opendata.nhs.scot/datastore/dump/967937c4-8d67-4f39-974f-fd58c4acfda5?format=json',

    # Infections
    "infections_daily": 'https://www.opendata.nhs.scot/datastore/dump/287fc645-4352-4477-9c8c-55bc054b7e76?format=json',
    "infections_daily_by_council": 'https://www.opendata.nhs.scot/datastore/dump/427f9a25-db22-4014-a3bc-893b68243055?format=json',
    "infections_total_by_council": 'https://www.opendata.nhs.scot/datastore/dump/e8454cf0-1152-4bcb-b9da-4343f625dfef?format=json',
    "infections_total_by_deprivation": 'https://www.opendata.nhs.scot/datastore/dump/a965ee86-0974-4c93-bbea-e839e27d7085?format=json',

    # Vaccines
    "vaccines_by_group": 'https://www.opendata.nhs.scot/datastore/dump/9b99e278-b8d8-47df-8d7a-a8cf98519ac1?format=json',
    "vaccines_total": 'https://www.opendata.nhs.scot/datastore/dump/42f17a3c-a4db-4965-ba68-3dffe6bca13a?format=json',
    "vaccines_by_council": 'https://www.opendata.nhs.scot/datastore/dump/d5ffffc0-f6f3-4b76-8f38-71ccfd7747a4?format=json',
}

conn = sqlite3.connect(database)

progress = 1
total = len(datasets.keys())

# Download all datasets
# Parse them and create tables
# Load data into tables
for table_name, url in datasets.items():
    file_name = os.path.join('/tmp', table_name + '.csv')
    print(f"[{progress}/{total}] Downloading {url} to {file_name}")
    os.system(f'curl --silent --location "{url}" --output "{file_name}" --max-time 450')

    cols = []
    with open(file_name, 'r') as file:
        contents = file.read()
        parsed = json.loads(contents)
        cols = [ "{} {}".format(field["id"], field["type"]) for field in parsed["fields"] ]
        cols = ','.join(cols)

        conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.cursor().execute(f"CREATE TABLE {table_name}({cols})")
        conn.commit()

        for row in parsed["records"]:
            placeholders = ','.join(['?'] * len(row))
            conn.cursor().execute(f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(row))
        conn.commit()

    progress += 1
