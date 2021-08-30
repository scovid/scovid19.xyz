from app.lib.OpenData import OpenData
from app.lib.Util import get_logger, strpstrf
from app.lib.data.Scotland import Scotland
from datetime import date, timedelta, datetime
from app.lib import DB


class Vaccines:
    def __init__(self):
        self.db = DB()
        self.logger = get_logger("app")
        self.scotland = Scotland()

    def summary(self):
        """
        Returns the vaccine figures for this last week and overall
        """
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')

        last_updated, = self.db.query('SELECT MAX(Date) FROM vaccines_total').fetchone()

        first_this_week, = self.db.query('SELECT SUM(NumberVaccinated) FROM vaccines_total WHERE product = "Total" AND AgeBand = "18 years and over" AND Dose = "Dose 1" AND Date >= :start', start=seven_days_ago).fetchone()
        second_this_week, = self.db.query('SELECT SUM(NumberVaccinated) FROM vaccines_total WHERE product = "Total" AND AgeBand = "18 years and over" AND Dose = "Dose 2" AND Date >= :start', start=seven_days_ago).fetchone()

        first_vax_total, = self.db.query('SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE product = "Total" AND AgeBand = "18 years and over" AND Dose = "Dose 1" ORDER BY Date DESC LIMIT 1').fetchone()
        fully_vaxxed_total, = self.db.query('SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE product = "Total" AND AgeBand = "18 years and over" AND Dose = "Dose 2" ORDER BY Date DESC LIMIT 1').fetchone()

        return {
            "this week": {
                "Dose 1": first_this_week,
                "Dose 2": second_this_week,
                "Week Ending": strpstrf(last_updated, strf="%d/%m/%Y"),
            },
            "totals": {
                "Dose 1": first_vax_total,
                "Dose 2": fully_vaxxed_total,
            },
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
        else:
            records = kwargs["records"]

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

        records = [ record for record in records if record["Product"] == "Total" and record["AgeBand"] == "All vaccinations" ]
        for record in records:
            if record["Dose"] == "Dose 1":
                totals["dose1"] += int(record["NumberVaccinated"])
            elif record["Dose"] == "Dose 2":
                totals["dose2"] += int(record["NumberVaccinated"])

        return totals

    def percentage_vaccinated(self):
        population = self.scotland.entire_population()

        totals = self.total_vaccinations()

        double_vax = totals["dose2"]
        single_vax = totals["dose1"] - totals["dose2"]
        no_vax = population - totals["dose1"]

        return {
            "labels": ["Both vaccines", "First vaccine only", "Un-vaccinated"],
            "datasets": [
                {
                    "backgroundColor": ["green", "lightblue", "red"],
                    "borderColor": ["green", "lightblue", "red"],
                    "label": "Vaccinations by total population",
                    "data": [ double_vax, single_vax, no_vax ],
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
