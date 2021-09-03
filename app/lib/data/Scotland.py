from app.lib.Decorators import cacheable
from app.lib.Util import get_logger
import app.lib.Cache as Cache
from app.lib import DB

# Heavy cacher for things that will rarely change
HEAVY_CACHER = Cache.Cacher(
    system=Cache.System.FILE,
    valid_for=Cache.Duration.days(2),
)


class Scotland:
    def __init__(self):
        self.db = DB()
        self.logger = get_logger("app")

    # Get the mapping of council IDs to council names
    @cacheable(cacher=HEAVY_CACHER)
    def councils(self):
        councils = self.db.query('SELECT CA, CAName FROM councils').fetchall()
        return { council["CA"]: council["CAName"] for council in councils }

    # Get the population of each council area for 2019
    @cacheable(cacher=HEAVY_CACHER)
    def population(self):
        rows = self.db.query('SELECT _id, Year, CA, Sex, AllAges FROM population_by_council WHERE CA != "S92000003" AND Sex = "All" AND Year = 2020').fetchall()
        return rows

    # Get the population for Scotland
    @cacheable(cacher=HEAVY_CACHER)
    def entire_population(self) -> int:
        population, = self.db.query('SELECT AllAges FROM population_by_council WHERE CA = "S92000003" AND Sex = "All" ORDER BY Year DESC LIMIT 1').fetchone()
        return int(population)
