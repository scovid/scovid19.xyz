"""
Tests for scovid19.lib.data using pytest
Uses the responses module to return dummy data to http requests
The mock responses are stored in scovid19/tests/responses/
"""

import pytest
import responses
import json
from scovid19.lib.data import Scotland, Infections, Vaccines


def read_response(name, as_json=True):
	with open(f"scovid19/tests/responses/{name}", "r") as f:
		if as_json:
			return json.loads(f.read())
		return f.read()


class TestScotland:
	@responses.activate
	def test_councils(self):
		responses.add(
			responses.GET,
			"https://www.opendata.nhs.scot/en/api/3/action/datastore_search?resource_id=967937c4-8d67-4f39-974f-fd58c4acfda5",
			json=read_response("councils.json", as_json=True),
			status=200,
		)

		scotland = Scotland()
		councils = scotland.councils()
		assert len(councils.keys()) == 36


class TestVaccines:
	@responses.activate
	def test_total_vaccinations(self):
		responses.add(
			responses.GET,
			"https://www.opendata.nhs.scot/en/api/3/action/datastore_search?resource_id=42f17a3c-a4db-4965-ba68-3dffe6bca13a&limit=1000",
			json=read_response("vaccines_daily.json", as_json=True),
			status=200,
		)

		vaccines = Vaccines()
		results = vaccines.total_vaccinations()
		assert "dose1" in results
		assert "dose2" in results
		assert results["dose1"] > 0
		assert results["dose2"] > 0


class TestInfections:
	@responses.activate
	def test_summary(self):
		responses.add(
			responses.GET,
			"https://www.opendata.nhs.scot/en/api/3/action/datastore_search?resource_id=287fc645-4352-4477-9c8c-55bc054b7e76&limit=1000&sort=Date%20ASC",
			json=read_response("infections_daily.json", as_json=True),
			status=200,
		)

		infections = Infections()
		results = infections.summary()
		assert "cases" in results
		assert "deaths" in results
