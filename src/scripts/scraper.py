#!/usr/bin/env python3

import os
import re
import sys
import json
import requests
import logging

from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(
	filename="/home/code/scovid19/logs/scraper.log",
	level=logging.INFO,
	format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)

URL='https://www.gov.scot/publications/coronavirus-covid-19-daily-data-for-scotland/'

def main():
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	html = requests.get(URL, headers = headers)
	parsed = BeautifulSoup(html.text, 'html.parser')

	summary = get_summary(parsed)

	dose1 = get_first_doses(summary)
	dose2 = get_second_doses(summary)

	date = datetime.today().strftime('%Y-%m-%d')

	content = json.dumps({ 'date': date, 'dose1': dose1, 'dose2': dose2 })

	write_file(content)

	return

def write_file(content):
	filepath = '/home/code/scovid19/data/vaccine.json'

	fh = open(filepath, "a")
	fh.write(content)
	fh.close()

	return


def get_summary(parsed):
	summary = parsed.find(class_="body-content publication-body").findAll('ul')[0].findAll('li')[5]

	return summary.find_all_next(string=True)

def get_first_doses(summary):
	return summary[0]

def get_second_doses(summary):
	return summary[3]

main()