import json
from lib.SCOVID import SCOVID
from lib.OpenData import OpenData
from datetime import datetime
import logging


class Vaccine(SCOVID):
	def __init__(self):
		self._cache = {}

	def vaccines_weekly(self):
		cases_by_week = OpenData.fetch("weekly_vaccine", limit=1000)
		records = cases_by_week["records"]

		latestrecords = []

		latestweek = records[-1]["WeekEnding"]
		for record in records:
			if record["WeekEnding"] == latestweek:
				latestrecords.append(record)

		councils = self.councils()
		totals = self.get_scraper_data() #self.get_totals(records)
		weekly = self.get_totals(latestrecords)
		return {
			"this week": {
				"Dose 1": weekly["dose1"],
				"Dose 2": weekly["dose2"],
				"Week Ending": datetime.strptime(
					str(records[-1]["WeekEnding"]), "%Y%m%d"
				).strftime("%d/%m/%Y"),
			},
			"totals": {"Dose 1": totals["dose1"], "Dose 2": totals["dose2"]},
		}

	def get_totals(self, records):
		totals = {
			"dose1": 0,
			"dose2": 0,
		}

		for record in records:
			# BUG: For some reason the AstraZeneca data has a blank number vaccinated
			if record["NumberVaccinated"].strip() == "":
				continue

			if record["Dose"] == "Dose 1":
				if record["NumberVaccinated"]:
					totals["dose1"] += int(record["NumberVaccinated"])
			elif record["Dose"] == "Dose 2":
				if record["NumberVaccinated"]:
					totals["dose2"] += int(record["NumberVaccinated"])

		return totals

	def percentage_vaccinated(self):
		population = self.scottish_population()

		#cases_by_week = OpenData.fetch("weekly_vaccine", limit=1000)
		#records = cases_by_week["records"]

		#totals = self.get_totals(records)
		totals = self.get_scraper_data()
		remainder = population - totals["dose2"] - totals["dose1"]

		dose1 = float(totals["dose1"] / population * 100)
		dose2 = float(totals["dose2"] / population * 100)
		remainder = float(remainder / population * 100)

		return {
			"labels": ["Second Dose received", "First Dose received", "Un-vaccinated"],
			"datasets": [
				{
					"backgroundColor": ["green", "lightblue", "red"],
					"borderColor": ["green", "lightblue", "red"],
					"label": "Vaccinations by total population",
					"data": [dose2, dose1, remainder],
				}
			],
		}

	def council_breakdown(self):
		council_vaccinations = OpenData.fetch("vaccine_council")
		records = council_vaccinations["records"]

		councils = self.councils()

		sets = []
		for location in records:
			if not location["CA"] or location["CA"] not in councils:
				continue

			sets.append({"x": councils[location["CA"]], "y": location["NumberVaccinated"]})

		sets = sorted(sets, key=lambda k: k["x"])
		return {
			"labels": sorted(set(councils.values())),
			"datasets": [
				{
					"backgroundColor": [Vaccine.color(item["x"]) for item in sets],
					"label": "Cases by area",
					"data": sets,
				}
			],
		}

	def vaccine_trend(self):
		cases_by_week = OpenData.fetch("weekly_vaccine")
		records = cases_by_week["records"]

		weeklydata = []
		for record in records:
			weekending = record["WeekEnding"]
			if weekending in weeklydata:
				continue

			weeklydata.append(weekending)

		dates = []
		dose1 = []
		dose2 = []

		for week in weeklydata:

			totals = {"dose1": 0, "dose2": 0}

			for record in records:
				if record["NumberVaccinated"].strip() == "":
					continue

				if week == record["WeekEnding"]:
					if record["Dose"] == "Dose 1":
						if record["NumberVaccinated"]:
							totals["dose1"] += int(record["NumberVaccinated"])
					elif record["Dose"] == "Dose 2":
						if record["NumberVaccinated"]:
							totals["dose2"] += int(record["NumberVaccinated"])

			dates.append(datetime.strptime(str(week), "%Y%m%d").strftime("%d/%m/%Y"))
			dose1.append(totals["dose1"])
			dose2.append(totals["dose2"])

		return {
			"labels": dates,
			"datasets": [
				{"label": "Dose 1", "backgroundColor": "lightblue", "data": dose1},
				{"label": "Dose 2", "backgroundColor": "lightgreen", "data": dose2},
			],
		}

	def get_scraper_data(self):
		filepath = "/home/code/scovid19/data/vaccine.json"

		with open(filepath) as fh:
			contents = json.loads(fh.read())
			
			return { 
				"dose1": int(contents['dose1']), 
				"dose2": int(contents['dose2']) 
			}

	@staticmethod
	def color(key):
		key = key.strip()

		color_map = {
			# Types
			"deaths": "#b3b3b3",
			"negative": "#b2df8a",
			"positive": "ff7f00",
			# Locations
			"Aberdeen City": "#33a02c",
			"Aberdeenshire": "#1f78b4",
			"Angus": "#b2df8a",
			"Argyll and Bute": "#a6cee3",
			"City of Edinburgh": "#fb9a99",
			"Clackmannanshire": "#e31a1c",
			"Dumfries and Galloway": "#fdbf6f",
			"Dundee City": "#ff7f00",
			"East Ayrshire": "#cab2d6",
			"East Dunbartonshire": "#6a3d9a",
			"East Lothian": "#ffff99",
			"East Renfrewshire": "#b15928",
			"Falkirk": "#66c2a5",
			"Fife": "#a6d854",
			# TODO: These need nicer colors
			"Glasgow City": "orangered",
			"Highland": "blue",
			"Inverclyde": "purple",
			"Midlothian": "cyan",
			"Moray": "pink",
			"Na h-Eileanan Siar": "burgandy",
			"North Ayrshire": "red",
			"North Lanarkshire": "yellow",
			"Orkney Islands": "lime",
			"Perth and Kinross": "rebeccapurple",
			"Renfrewshire": "brown",
			"Scottish Borders": "lightblue",
			"Shetland Islands": "navy",
			"South Ayrshire": "green",
			"South Lanarkshire": "orange",
			"Stirling": "darkgreen",
			"West Dunbartonshire": "grey",
			"West Lothian": "magenta",
		}

		return color_map[key] if key in color_map else "yellow"
