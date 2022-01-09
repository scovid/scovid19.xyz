from app.lib.Util import strpstrf, get_logger
from datetime import datetime, timedelta
from app.lib import DB

# TODO:
# - Confirm @cacheable decorator works
# - Add heavier caching for things that won't change


class Infections:
    def __init__(self):
        self.db = DB()
        self.logger = get_logger("app")

    # Return the summary of stats
    def summary(self):
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")

        (cases_this_week,) = self.db.query(
            "SELECT SUM(DailyCases) FROM cases WHERE `Date` >= :start_date",
            start_date=seven_days_ago,
        ).fetchone()
        (total_cases,) = self.db.query("SELECT CumulativeCases FROM cases ORDER BY `Date` DESC LIMIT 1").fetchone()
        most_cases = self.db.query("SELECT MAX(DailyCases), Date FROM cases").fetchone()
        (total_deaths,) = self.db.query("SELECT MAX(Deaths) FROM cases").fetchone()

        # We do not have the daily death stats, only the total at any given date
        # So go through all records
        most_deaths = (0, "")
        total_deaths_yesterday = 0
        deaths_this_week = 0
        records = self.db.query("SELECT `Date`, Deaths FROM cases ORDER BY `Date` ASC")
        for record in records.fetchall():
            date, total_deaths = record
            deaths_today = total_deaths - total_deaths_yesterday
            if deaths_today > int(most_deaths[0]):
                most_deaths = (deaths_today, date)
            total_deaths_yesterday = total_deaths

            if date >= int(seven_days_ago):
                deaths_this_week += deaths_today

        return {
            "cases": {
                "total": total_cases,
                "new": cases_this_week,
                "avg": int(round(cases_this_week / 7)),
                "most": {
                    "number": most_cases[0],
                    "date": strpstrf(most_cases[1]),
                },
            },
            "deaths": {
                "total": total_deaths,
                "new": deaths_this_week,
                "avg": int(round(deaths_this_week / 7)),
                "most": {
                    "number": most_deaths[0],
                    "date": strpstrf(most_deaths[1]),
                },
            },
        }

    # Return the overall cases by day for Scotland
    def trend(self, start=None, end=None):
        """
        Returns the data for the daily infections trend chart
        """
        start, end = self.get_date_range(start, end)

        rows = self.db.query(
            "SELECT `Date`, DailyCases FROM cases WHERE `Date` >= :start AND `Date` <= :end",
            start=start,
            end=end,
        )

        dates = []
        cases = []
        for day in rows:
            date = strpstrf(str(day["Date"]), strf="%d %b %y")
            dates.append(date)
            cases.append(day["DailyCases"])

        return {
            "labels": dates,
            "datasets": [{"backgroundColor": "darkorange", "label": "Positive", "data": cases}],
        }

    def breakdown(self):
        """
        Breakdown of postive, negative and deaths over the full time period
        """
        positive, negative, deaths = self.db.query(
            "SELECT SUM(TotalPositive), SUM(TotalNegative), SUM(TotalDeaths) FROM cases_by_deprivation"
        ).fetchone()

        return {
            "labels": ["Positive", "Negative", "Deaths"],
            "datasets": [
                {
                    "backgroundColor": ["darkorange", "lightgreen", "darkgrey"],
                    "borderColor": ["darkorange", "lightgreen", "darkgrey"],
                    "label": "Breakdown",
                    "data": [positive, negative, deaths],
                }
            ],
        }

    def by_age(self):
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")
        rows = self.db.query(
            'SELECT AgeGroup, DailyPositive FROM cases_by_age WHERE Sex = "Total" AND Date > :start AND AgeGroup NOT IN ("Total", "0 to 59", "60+") GROUP BY AgeGroup',
            start=seven_days_ago,
        ).fetchall()

        return {
            "labels": [row["AgeGroup"] for row in rows],
            "datasets": [
                {
                    "label": "Cases",
                    "backgroundColor": "darkorange",
                    "data": [row["DailyPositive"] for row in rows],
                },
            ],
        }

    def hospital_admissions(self, start=None, end=None):
        start, end = self.get_date_range(start, end)

        rows = self.db.query(
            "SELECT Date, NumberAdmitted FROM hospital_admissions WHERE `Date` >= :start AND `Date` <= :end ORDER BY Date DESC",
            start=start,
            end=end,
        ).fetchall()

        return {
            "labels": [strpstrf(str(row["Date"]), strf="%d %b %y") for row in reversed(rows)],
            "datasets": [
                {
                    "label": "Cases",
                    "backgroundColor": "lightblue",
                    "data": [row["NumberAdmitted"] for row in reversed(rows)],
                },
            ],
        }

    def prevalence(self):
        """
        Returns the cases per 100k for each council area
        """
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")
        prevalence = []

        rows = self.db.query(
            'SELECT c.CAName, SUM(i.DailyPositive) AS Positive, pop.AllAges AS Population FROM cases_by_council AS i LEFT JOIN councils AS c ON i.CA = c.CA LEFT JOIN population_by_council AS pop ON pop.CA = c.CA WHERE i.Date >= :start AND pop.Sex = "All" AND pop.year = 2020 GROUP BY i.CA',
            start=seven_days_ago,
        )

        for row in rows:
            quotient = row["Population"] / 100_000
            per_100k = row["Positive"] / quotient

            prevalence.append(
                {
                    "council": row["CAName"],
                    "population": format(row["Population"], ","),
                    "cases": format(row["Positive"], ","),
                    "per_100k": round(per_100k, 2),
                    "percentage": format(row["Positive"] / row["Population"], ","),
                }
            )

        return sorted(prevalence, key=lambda x: x["per_100k"], reverse=True)

    def last_updated(self, format=None):
        """
        Returns the last date in the infections_daily data
        """
        (last_updated,) = self.db.query("SELECT MAX(`Date`) FROM cases").fetchone()
        last_updated = datetime.strptime(str(last_updated), "%Y%m%d")

        if format:
            return datetime.strftime(last_updated, format)

        return last_updated

    @staticmethod
    def get_date_range(start: str = "", end: str = "", default_days: int = 30):
        """
        Take a start and end date in the format YYYY-MM-DD
        Return them in the format YYYYMMDD

        If they are blank then default to start=today, end=30 days ago
        """
        if start and end:
            start = strpstrf(start, rev=True)
            end = strpstrf(end, rev=True)
        else:
            start = (datetime.today() - timedelta(days=default_days)).strftime("%Y%m%d")
            end = datetime.today().strftime("%Y%m%d")

        return start, end

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
