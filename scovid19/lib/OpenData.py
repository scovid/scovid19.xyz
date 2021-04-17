import sys
import requests
import logging
import scovid19.lib.Cache as Cache
from scovid19.lib.Decorators import cacheable

# Define our cache
# File cacher with an expiry of 2 hours
CACHER = Cache.Cacher(system=Cache.System.FILE, valid_for=Cache.Duration.hours(2))


class OpenData:
	default_timeout = 5
	endpoint = "https://www.opendata.nhs.scot/en/api/3/action/datastore_search"

	resources = {
		# Infections
		"daily": "287fc645-4352-4477-9c8c-55bc054b7e76",  # Daily and Cumulative Cases
		"total_by_area": "e8454cf0-1152-4bcb-b9da-4343f625dfef",  # Total Cases By Council Area
		"daily_by_area": "427f9a25-db22-4014-a3bc-893b68243055",  # Daily Case Trends By Council Area
		"total_by_deprivation": "a965ee86-0974-4c93-bbea-e839e27d7085",  # Total Cases By Deprivation
		# Vaccine
		"daily_vaccine": "42f17a3c-a4db-4965-ba68-3dffe6bca13a",  # Daily vaccinations
		"weekly_vaccine": "93a86415-9b3e-488a-ba50-1a70793a3208",  # Weekly vaccinations
		"vaccine_council": "4ec38438-c8b3-4946-9283-ee99f7a86a3b",  # Vaccinations by council area
		# Other
		"councils": "967937c4-8d67-4f39-974f-fd58c4acfda5",  # Mapping of council ID to name
		"population": "09ebfefb-33f4-4f6a-8312-2d14e2b02ace",  # Population by council
	}

	@staticmethod
	@cacheable(cacher=CACHER)
	def fetch(resource, **kwargs):
		if resource not in OpenData.resources:
			logging.error(f"ERROR: Requested resource '{resource}' is not valid")
			return {}

		kwargs["resource_id"] = OpenData.resources[resource]
		r = requests.get(OpenData.endpoint, timeout=OpenData.default_timeout, params=kwargs)

		if r.status_code != 200:
			logging.error(f"ERROR: Bad response from OpenData API:\n{r.content}")
			return {}

		json = r.json()
		return json["result"]

	# Util method to just return the records from fetch()
	@staticmethod
	def fetch_records(resource, **kwargs):
		results = OpenData.fetch(resource, **kwargs)

		if "records" in results:
			return results["records"]

		logging.error(f"ERROR: OpenData API did not return any records:\n{results}")
		return {}
