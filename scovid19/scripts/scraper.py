#!/usr/bin/env python3

import os, re, sys, json
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(
	filename=os.environ["PROJECT_ROOT"] + "/logs/scraper.log",
	level=logging.INFO,
	format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)

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
	except:
		logging.error("Error scraping doses")
		exit(1)

	date = datetime.today().strftime("%Y-%m-%d")

	content = json.dumps({"date": date, "dose1": dose1, "dose2": dose2})

	write_file(content)

	return


def write_file(content):
	filepath = os.environ["PROJECT_ROOT"] + "/data/vaccine.json"

	fh = open(filepath, "w", encoding="utf8")
	fh.write(content)
	fh.close()

	return


def get_summary(parsed):
	summary = (
		parsed.find(class_="body-content publication-body").findAll("ul")[0].findAll("li")[5]
	)

	return summary.find_all_next(string=True)


def get_first_doses(summary):
	dose1 = clean_str(summary[0].replace(",", ""))
	return dose1


def get_second_doses(summary):
	dose2 = clean_str(summary[3].replace(",", ""))

	if not dose2: # This is where the fun begins
		if summary[4]:
			dose2 = clean_str(summary[4].replace(",", ""))
		else:
			first, *middle, last = summary[1].split()
			dose2 = clean_str(last + summary[2].replace(",", ""))

	return dose2


def clean_str(string):
	if not string:
		return ""
	return str(string).strip().replace(u"\u00a0", " ")


main()
