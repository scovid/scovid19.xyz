import json
from scovid19.lib.OpenData import OpenData
from scovid19.lib.Util import project_root, get_logger
from scovid19.lib.data.Scotland import Scotland
from datetime import date, timedelta, datetime


class Vaccines:
    def __init__(self):
        self.logger = get_logger("app")
        self.scotland = Scotland()

    def vaccines_summary(self):
        """
        Returns the vaccine figures for this last week and overall
        """
        totals = self.total_vaccinations()

        start, end = self.get_previous_week()
        weekly_records = self.get_weekly_data(start, end)
        weekly = self.get_totals(weekly_records)

        return {
            "this week": {
                "Dose 1": weekly["dose1"],
                "Dose 2": weekly["dose2"],
                "Week Ending": end.strftime("%d/%m/%Y"),
            },
            "totals": {"Dose 1": totals["dose1"], "Dose 2": totals["dose2"]},
        }

    def total_vaccinations(self):
        """
        Returns the total vaccinated overall
        """
        daily_cases = self.get_daily_data()
        return self.get_totals(daily_cases)

    def get_daily_data(self):
        cases_by_day = OpenData.fetch("daily_vaccine", limit=10000)
        records = cases_by_day["records"]

        return records

    def get_weekly_data(self, start, end, **kwargs):
        if "records" not in kwargs:
            records = self.get_daily_data()

        start = str(start).replace("-", "")
        end = str(end).replace("-", "")

        weekly_records = []

        for record in records:
            if int(start) <= int(record["Date"]) <= int(end):
                weekly_records.append(record)

        return weekly_records

    def get_previous_week(self, **kwargs):
        if "starting_date" not in kwargs:
            starting_date = date.today()
        else:
            starting_date = datetime.strptime(
                str(kwargs["starting_date"]), "%Y%m%d"
            ).date()

        start = starting_date - timedelta(days=starting_date.weekday(), weeks=+1)
        end = start + timedelta(days=6)

        return start, end

    def get_totals(self, records):
        totals = {
            "dose1": 0,
            "dose2": 0,
        }

        for record in records:
            if (
                record["Product"] == "Total"
                and record["AgeBand"] == "16 years and over"
            ):
                if record["Dose"] == "Dose 1":
                    totals["dose1"] += int(record["NumberVaccinated"])
                elif record["Dose"] == "Dose 2":
                    totals["dose2"] += int(record["NumberVaccinated"])

        return totals

    def percentage_vaccinated(self):
        population = self.scotland.entire_population()

        totals = self.total_vaccinations()
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

        sets = []
        councils = self.scotland.councils()
        for location in records:
            if not location["CA"] or location["CA"] not in councils:
                continue

            sets.append(
                {"x": councils[location["CA"]], "y": location["NumberVaccinated"]}
            )

        sets = sorted(sets, key=lambda k: k["x"])
        return {
            "labels": sorted(set(councils.values())),
            "datasets": [
                {
                    "backgroundColor": [Vaccines.color(item["x"]) for item in sets],
                    "label": "Cases by area",
                    "data": sets,
                }
            ],
        }

    def vaccine_trend(self):
        total_cases = self.get_daily_data()

        weeks = []
        dates = []

        for case in total_cases:  # a list of when each week starts and ends
            if case["Product"] == "Total":
                start, end = self.get_previous_week(starting_date=case["Date"])

                if str(start) != "2020-11-30":
                    week = {"start": start, "end": end}

                    if week not in weeks:
                        weeks.append({"start": start, "end": end})
                        dates.append(start.strftime("%d/%m/%Y"))

        dose1 = []
        dose2 = []

        for record in weeks:  # Get the total weekly data for these ranges
            weekly_records = self.get_weekly_data(record["start"], record["end"])
            weekly_totals = self.get_totals(weekly_records)

            dose1.append(weekly_totals["dose1"])
            dose2.append(weekly_totals["dose2"])

        return {
            "labels": dates,
            "datasets": [
                {"label": "Dose 1", "backgroundColor": "lightblue", "data": dose1},
                {"label": "Dose 2", "backgroundColor": "lightgreen", "data": dose2},
            ],
        }

    def get_scraper_data(self):
        filepath = f"{project_root()}/data/vaccine.json"

        with open(filepath) as fh:
            contents = json.loads(fh.read())

            return {"dose1": int(contents["dose1"]), "dose2": int(contents["dose2"])}

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
