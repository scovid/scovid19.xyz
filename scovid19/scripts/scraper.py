#!/usr/bin/env python3

import os, re, sys, json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from scovid19.lib.Util import get_logger, project_root

scraper_logger = get_logger("scraper")

URL = "https://www.gov.scot/publications/coronavirus-covid-19-daily-data-for-scotland/"


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    html = requests.get(URL, headers=headers)
    parsed = BeautifulSoup(html.text, "html.parser")

    summary = get_summary(parsed)

    try:
        dose1 = get_first_doses(summary)
        dose2 = get_second_doses(summary)
    except ValueError as e:
        scraper_logger.error(e)
        exit(1)
    except Exception as e:
        scraper_logger.error(e)

    date = datetime.today().strftime("%Y-%m-%d")

    content = json.dumps({"date": date, "dose1": dose1, "dose2": dose2})

    write_file(content)

    return


def write_file(content):
    filepath = f"{project_root()}/data/vaccine.json"

    fh = open(filepath, "w", encoding="utf8")
    fh.write(content)
    fh.close()

    return


def get_summary(parsed):
    summary = (
        parsed.find(class_="body-content publication-body")
        .findAll("ul")[0]
        .findAll("li")[5]
    )

    return summary.find_all_next(string=True)


def get_first_doses(summary):
    if "\n" in summary[0]:
        dose1 = clean_str(summary[1].partition(" ")[0].replace(",", ""))
    else:
        dose1 = clean_str(summary[0].replace(",", ""))

    if not dose1:
        raise ValueError("dose 1 is empty")
    else:
        return dose1


def get_second_doses(summary):
    if "\n" in summary[0]:
        dose2 = clean_str(summary[1].split()[12].replace(",", ""))
    else:
        dose2 = clean_str(summary[3].replace(",", ""))

    if not dose2:  # This is where the fun begins
        if summary[4]:
            dose2 = clean_str(summary[4].replace(",", ""))
        else:
            first, *middle, last = summary[1].split()
            dose2 = clean_str(last + summary[2].replace(",", ""))

    if not dose2:
        raise ValueError("dose 2 is empty")
    else:
        return dose2


def clean_str(string):
    if not string:
        return ""
    return str(string).strip().replace("\u00a0", " ")


main()
