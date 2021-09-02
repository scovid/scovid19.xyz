from app.lib.Util import get_logger, strpstrf
from app.lib.data.Scotland import Scotland
from datetime import timedelta, datetime
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

    def percentage_vaccinated(self):
        population = self.scotland.entire_population()

        double_vax, = self.db.query('SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE AgeBand = "18 years and over" AND Dose = "Dose 2" ORDER BY Date DESC LIMIT 1').fetchone()
        single_vax, = self.db.query('SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE AgeBand = "18 years and over" AND Dose = "Dose 1" ORDER BY Date DESC LIMIT 1').fetchone()
        no_vax = population - single_vax

        single_vax -= double_vax

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

    def trend(self):
        today = datetime.today()
        start = datetime(year=2020, month=12, day=8)
        week = start

        weeks = []
        dates = []

        dose1 = []
        dose2 = []

        while week < today:
            next_week = week + timedelta(days=7)

            first_dose, = self.db.query('SELECT SUM(NumberVaccinated) AS NumberVaccinated FROM vaccines_total WHERE AgeBand = "18 years and over" AND Date >= :week AND Date < :next_week AND Dose = "Dose 1"', week=week.strftime('%Y%m%d'), next_week=next_week.strftime('%Y%m%d')).fetchone()
            second_dose, = self.db.query('SELECT SUM(NumberVaccinated) AS NumberVaccinated FROM vaccines_total WHERE AgeBand = "18 years and over" AND Date >= :week AND Date < :next_week AND Dose = "Dose 2"', week=week.strftime('%Y%m%d'), next_week=next_week.strftime('%Y%m%d')).fetchone()

            if not first_dose or not second_dose:
                break

            weeks.append({ "start": week, "end": next_week })
            dates.append(week.strftime("%d/%m/%Y"))

            dose1.append(first_dose)
            dose2.append(second_dose)

            week = next_week

        return {
            "labels": dates,
            "datasets": [
                { "label": "First Vaccine", "backgroundColor": "lightblue", "data": dose1 },
                { "label": "Second Vaccine", "backgroundColor": "lightgreen", "data": dose2 },
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
