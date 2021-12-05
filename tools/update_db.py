#!/usr/bin/env python3

"""
This script will download all of the configured datasets and load them into an sqlite3 file database
First downloads the JSON to get the schema, then downloads the CSV to load the data
The JSON has the data but a few datasets have incorrect JSON data but correct CSV so just always use the CSV
"""

import sqlite3
import json
import csv
import os
from pathlib import Path

# https://www.opendata.nhs.scot/dataset/covid-19-in-scotland
# https://www.opendata.nhs.scot/dataset/covid-19-vaccination-in-scotland
# https://www.opendata.nhs.scot/dataset/weekly-covid-19-statistical-data-in-scotland
datasets = {
    # Misc
    "population_by_council": "https://www.opendata.nhs.scot/datastore/dump/09ebfefb-33f4-4f6a-8312-2d14e2b02ace",
    "councils": "https://www.opendata.nhs.scot/datastore/dump/967937c4-8d67-4f39-974f-fd58c4acfda5",
    # Infections
    "cases": "https://www.opendata.nhs.scot/datastore/dump/287fc645-4352-4477-9c8c-55bc054b7e76",
    "cases_by_council": "https://www.opendata.nhs.scot/datastore/dump/427f9a25-db22-4014-a3bc-893b68243055",
    "cases_by_deprivation": "https://www.opendata.nhs.scot/datastore/dump/a965ee86-0974-4c93-bbea-e839e27d7085",
    "cases_by_age": "https://www.opendata.nhs.scot/datastore/dump/9393bd66-5012-4f01-9bc5-e7a10accacf4",
    # Vaccines
    "vaccines_by_group": "https://www.opendata.nhs.scot/datastore/dump/9b99e278-b8d8-47df-8d7a-a8cf98519ac1",
    "vaccines_total": "https://www.opendata.nhs.scot/datastore/dump/42f17a3c-a4db-4965-ba68-3dffe6bca13a",
    "vaccines_by_council": "https://www.opendata.nhs.scot/datastore/dump/d5ffffc0-f6f3-4b76-8f38-71ccfd7747a4",
    # Hospital admissions
    "hospital_admissions": "https://www.opendata.nhs.scot/datastore/dump/0451bc49-0eaf-49a0-aa76-7f4539e5a615",
}

database = Path("./data/scovid19.db")
database.parent.mkdir(parents=True, exist_ok=True)
database.touch()

conn = sqlite3.connect(str(database))


def main():
    progress = 1
    total = len(datasets.keys())

    # Download all datasets
    # Parse them and create tables
    # Load data into tables
    for table_name, url in datasets.items():
        print(f"[{progress}/{total}] Loading {table_name}")

        # Download the JSON to get the schema
        json_file = download(url, "json")
        create_table(json_file, table_name)

        # Download the CSV to load the data
        csv_file = download(url, "csv")
        load_csv(csv_file, table_name)

        os.remove(json_file)
        os.remove(csv_file)
        progress += 1


def download(url, format):
    """
    Downloads a file to /tmp, returns the path to the file
    """
    import tempfile

    file = tempfile.NamedTemporaryFile(delete=False)

    url = f"{url}?format={format}"

    print(f"Downloading {url} to {file.name}")
    os.system(f'curl --silent --location "{url}" --output "{file.name}" --max-time 450')

    return file.name


def create_table(json_file, table_name):
    with open(json_file, "r") as file:
        contents = file.read()
        parsed = json.loads(contents)
        cols = ["{} {}".format(field["id"], field["type"]) for field in parsed["fields"]]
        cols = ",".join(cols)

        conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.cursor().execute(f"CREATE TABLE {table_name}({cols})")
        conn.commit()


def load_csv(csv_file, table_name):
    with open(csv_file, "r") as data:
        reader = csv.reader(data)
        next(reader)  # Consume header row
        for row in reader:
            placeholders = ",".join(["?"] * len(row))
            conn.cursor().execute(f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(row))
    conn.commit()


if __name__ == "__main__":
    main()
