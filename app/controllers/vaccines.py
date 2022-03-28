from app.lib.Util import get_logger, strpstrf
from app.controllers import Scotland
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
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")

        (last_updated,) = self.db.query(
            "SELECT MAX(Date) FROM vaccines_total"
        ).fetchone()

        (first_this_week,) = self.db.query(
            'SELECT SUM(NumberVaccinated) FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 1" AND Date >= :start',
            start=seven_days_ago,
        ).fetchone()
        (second_this_week,) = self.db.query(
            'SELECT SUM(NumberVaccinated) FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 2" AND Date >= :start',
            start=seven_days_ago,
        ).fetchone()
        (third_this_week,) = self.db.query(
            'SELECT SUM(NumberVaccinated) FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 3" AND Date >= :start',
            start=seven_days_ago,
        ).fetchone()

        (single_vax_total,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 1" ORDER BY Date DESC LIMIT 1'
        ).fetchone()
        (double_vax_total,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 2" ORDER BY Date DESC LIMIT 1'
        ).fetchone()
        (triple_vax_total,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE product = "Total" AND AgeBand = "All vaccinations" AND Dose = "Dose 3" ORDER BY Date DESC LIMIT 1'
        ).fetchone()

        return {
            "this week": {
                "Dose 1": first_this_week,
                "Dose 2": second_this_week,
                "Dose 3": third_this_week,
                "Week Ending": strpstrf(last_updated, strf="%d/%m/%Y"),
            },
            "totals": {
                "Dose 1": single_vax_total,
                "Dose 2": double_vax_total,
                "Dose 3": triple_vax_total,
            },
        }

    def percentage(self):
        population = self.scotland.population_for_age_range(lower=12)

        (triple_vax,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Dose = "Dose 3" AND Product = "Total" ORDER BY Date DESC LIMIT 1'
        ).fetchone()
        (double_vax,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Dose = "Dose 2" AND Product = "Total" ORDER BY Date DESC LIMIT 1'
        ).fetchone()
        (single_vax,) = self.db.query(
            'SELECT CumulativeNumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Dose = "Dose 1" AND Product = "Total" ORDER BY Date DESC LIMIT 1'
        ).fetchone()
        no_vax = population - single_vax

        single_vax -= double_vax
        double_vax -= triple_vax

        return {
            "labels": [
                "Three Vaccines",
                "Two Vaccines Only",
                "One Vaccine Only",
                "No Vaccines",
            ],
            "datasets": [
                {
                    "backgroundColor": ["green", "yellow", "orange", "red"],
                    "borderColor": ["green", "yellow", "orange", "red"],
                    "label": "Vaccinations by total population (12+)",
                    "data": [triple_vax, double_vax, single_vax, no_vax],
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
        dose3 = []

        while week < today:
            next_week = week + timedelta(days=7)

            (first_dose,) = self.db.query(
                'SELECT SUM(NumberVaccinated) AS NumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Date >= :week AND Date < :next_week AND Dose = "Dose 1" AND Product = "Total"',
                week=week.strftime("%Y%m%d"),
                next_week=next_week.strftime("%Y%m%d"),
            ).fetchone()
            (second_dose,) = self.db.query(
                'SELECT SUM(NumberVaccinated) AS NumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Date >= :week AND Date < :next_week AND Dose = "Dose 2" AND Product = "Total"',
                week=week.strftime("%Y%m%d"),
                next_week=next_week.strftime("%Y%m%d"),
            ).fetchone()
            (third_dose,) = self.db.query(
                'SELECT SUM(NumberVaccinated) AS NumberVaccinated FROM vaccines_total WHERE AgeBand = "All vaccinations" AND Date >= :week AND Date < :next_week AND Dose = "Dose 3" AND Product = "Total"',
                week=week.strftime("%Y%m%d"),
                next_week=next_week.strftime("%Y%m%d"),
            ).fetchone()

            weeks.append({"start": week, "end": next_week})
            dates.append(week.strftime("%d/%m/%Y"))

            dose1.append(first_dose)
            dose2.append(second_dose)
            dose3.append(third_dose)

            week = next_week

        return {
            "labels": dates,
            "datasets": [
                {
                    "label": "First Vaccine",
                    "backgroundColor": "orange",
                    "data": dose1,
                },
                {
                    "label": "Second Vaccine",
                    "backgroundColor": "yellow",
                    "data": dose2,
                },
                {
                    "label": "Third Vaccine",
                    "backgroundColor": "green",
                    "data": dose3,
                },
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
