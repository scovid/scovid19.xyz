from app.lib.Decorators import cacheable
from app.lib.Util import get_logger
import app.lib.Cache as Cache
from app.lib import DB

# Heavy cacher for things that will rarely change
HEAVY_CACHER = Cache.Cacher(
    system=Cache.System.FILE,
    valid_for=Cache.Duration.days(2),
)

MAX_YEAR = 2020
COUNTRY_CA = "S92000003"  # The CA for Scotland as a country


class Scotland:
    def __init__(self):
        self.db = DB()
        self.logger = get_logger("app")

    # Get the mapping of council IDs to council names
    @cacheable(cacher=HEAVY_CACHER)
    def councils(self):
        councils = self.db.query("SELECT CA, CAName FROM councils").fetchall()
        return {council["CA"]: council["CAName"] for council in councils}

    # Get the population of each council area for 2019
    @cacheable(cacher=HEAVY_CACHER)
    def population_per_council(self):
        rows = self.db.query(
            'SELECT _id, Year, CA, Sex, AllAges FROM population_by_council WHERE CA != :scotland AND Sex = "All" AND Year = :year',
            year=MAX_YEAR,
            scotland=COUNTRY_CA,
        ).fetchall()
        return rows

    # Get the population for Scotland
    @cacheable(cacher=HEAVY_CACHER)
    def population(self) -> int:
        (population,) = self.db.query(
            'SELECT AllAges FROM population_by_council WHERE CA = :scotland AND Sex = "All" ORDER BY Year DESC LIMIT 1',
            scotland=COUNTRY_CA,
        ).fetchone()
        return int(population)

    # Get the population of Scotland for an age range
    @cacheable(cacher=HEAVY_CACHER)
    def population_for_age_range(self, lower=0, upper=90):
        lower = 0 if lower < 0 else lower
        upper = 90 if upper > 90 else upper

        columns = " + ".join(["Age{}".format(age) for age in range(lower, upper)])
        columns = columns.replace("Age90", "Age90Plus")

        (population,) = self.db.query(
            f'SELECT {columns} FROM population_by_council WHERE CA = "S92000003" AND Sex = "All" AND Year = :year',
            year=MAX_YEAR,
        ).fetchone()
        return int(population)
