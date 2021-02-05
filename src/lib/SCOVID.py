from lib.OpenData import OpenData
from lib.Decorators import cacheable


class SCOVID:
	def __init__(self):
		self._cache = {}

	# Get the mapping of council IDs to council names
	@cacheable
	def councils(self):
		councils = OpenData.fetch("councils")
		return {council["CA"]: council["CAName"] for council in councils["records"]}

	# Get the population of each council area for 2019
	@cacheable
	def population(self):
		populations = OpenData.fetch("population", limit=10000)["records"]
		return [x for x in populations if x["Year"] == 2019 and x["Sex"] == "All"]

	# Get the population for Scotland
	@cacheable
	def scottish_population(self):
		populations = self.population()
		
		for pop in populations:
			if pop['CA'] == 'S92000003':
				return int(pop['AllAges'])