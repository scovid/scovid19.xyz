from scovid19.lib.OpenData import OpenData
from scovid19.lib.Decorators import cacheable
import scovid19.lib.Cache as Cache

# Heavy cacher for things that will rarely change
HEAVY_CACHER = Cache.Cacher(
	system=Cache.System.FILE,
	valid_for=Cache.Duration.days(2),
	is_method=True,
)

class SCOVID:
	def __init__(self):
		self._cache = {}

	# Get the mapping of council IDs to council names
	@cacheable(cacher=HEAVY_CACHER)
	def councils(self):
		councils = OpenData.fetch("councils")
		return {council["CA"]: council["CAName"] for council in councils["records"]}

	# Get the population of each council area for 2019
	@cacheable(cacher=HEAVY_CACHER)
	def population(self):
		populations = OpenData.fetch("population", limit=10000)["records"]
		return [x for x in populations if x["Year"] == 2019 and x["Sex"] == "All"]

	# Get the population for Scotland
	@cacheable(cacher=HEAVY_CACHER)
	def scottish_population(self):
		populations = self.population()

		for pop in populations:
			if pop["CA"] == "S92000003":
				return int(pop["AllAges"])
