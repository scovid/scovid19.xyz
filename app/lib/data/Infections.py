from app.lib.data.Scotland import Scotland
from app.lib.OpenData import OpenData
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
        self.scotland = Scotland()

    # Return the summary of stats
    def summary(self):
        seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')

        cases_this_week, = self.db.query('SELECT SUM(DailyCases) FROM infections_daily WHERE `Date` >= :start_date', start_date=seven_days_ago).fetchone()
        total_cases, = self.db.query('SELECT CumulativeCases FROM infections_daily ORDER BY `Date` DESC LIMIT 1').fetchone()
        most_cases = self.db.query('SELECT MAX(DailyCases), Date FROM infections_daily').fetchone()
        total_deaths, = self.db.query('SELECT MAX(Deaths) FROM infections_daily').fetchone()

        # We do not have the daily death stats, only the total at any given date
        # So go through all records
        most_deaths = (0, '')
        deaths_yesterday = 0
        deaths_this_week = 0
        records = self.db.query('SELECT `Date`, Deaths FROM infections_daily ORDER BY `Date` ASC')
        for record in records.fetchall():
            date, deaths = record
            deaths_today = deaths - deaths_yesterday
            if deaths_today > int(most_deaths[0]):
                most_deaths = (deaths_today, date)
            deaths_yesterday = deaths

            if date >= int(seven_days_ago):
                deaths_this_week += deaths_yesterday

        return {
            "cases": {
                "total": total_cases,
                "new": cases_this_week,
                "avg": int(round(cases_this_week / 7)),
                "most": {
                    "number": most_cases[0],
                    "date": strpstrf(most_cases[1]),
                }
            },
            "deaths": {
                "total": total_deaths,
                "new": deaths_this_week,
                "avg": int(round(deaths_this_week / 7)),
                "most": {
                    "number": most_deaths[0],
                    "date": strpstrf(most_deaths[1]),
                }
            }
        }

    # Return the overall cases by day for Scotland
    def trend(self, params={}):
        if "start" in params and "end" in params:
            start = strpstrf(params["start"], rev=True)
            end = strpstrf(params["end"], rev=True)
        else:
            start = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')
            end = datetime.today().strftime('%Y%m%d')

        rows = self.db.query('SELECT `Date`, DailyCases FROM infections_daily WHERE `Date` >= :start AND `Date` <= :end', start=start, end=end)

        dates = []
        cases = []
        for day in rows:
            date = strpstrf(str(day["Date"]), strf="%d %b %y")
            dates.append(date)
            cases.append(day["DailyCases"])

        return {
            "labels": dates,
            "datasets": [
                {"backgroundColor": "darkorange", "label": "Positive", "data": cases}
            ],
        }

    def breakdown(self):
        """
        Breakdown of postive, negative and deaths over the full time period
        """
        positive, negative, deaths = self.db.query("SELECT SUM(TotalPositive), SUM(TotalNegative), SUM(TotalDeaths) FROM infections_total_by_deprivation").fetchone()

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

    def prevalence(self):
        councils = self.scotland.councils()
        populations = self.scotland.population()

        # Fetch the daily trends by council for the last 7 days
        daily_by_area = OpenData.fetch(
            "daily_by_area", limit=(len(councils) * 7), sort="Date DESC"
        )["records"]

        # Total up the cases
        cases = {}
        for record in daily_by_area:
            if record["CA"] not in cases:
                cases[record["CA"]] = 0
            cases[record["CA"]] += record["DailyPositive"]

        prevalence = []
        for pop in populations:
            if pop["CA"] not in councils:
                continue

            # Work out cases per 100k people
            quotient = pop["AllAges"] / 100_000
            per_100k = cases[pop["CA"]] / quotient

            prevalence.append(
                {
                    "council": councils[pop["CA"]],
                    "population": format(pop["AllAges"], ","),
                    "cases": format(cases[pop["CA"]], ","),
                    "per_100k": round(per_100k, 2),
                    "percentage": format(cases[pop["CA"]] / pop["AllAges"], ","),
                }
            )

        return sorted(prevalence, key=lambda x: x["per_100k"], reverse=True)

    # Get the last updated time of the OpenData stats
    # Based on the latest date in the "Daily and Cumulative Cases" data set
    def last_updated(self, format=None):
        last_updated, = self.db.query('SELECT MAX(`Date`) FROM infections_daily').fetchone()
        last_updated = datetime.strptime(str(last_updated), "%Y%m%d")

        if format:
            return datetime.strftime(last_updated, format)

        return last_updated

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
