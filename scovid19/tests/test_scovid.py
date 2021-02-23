"""
Tests for SCOVID.py using pytest
Uses the responses module to return dummy data to http requests
The mock responses are stored in scovid19/tests/responses/
"""

import pytest
import responses
import json
from scovid19.lib.Infections import Infections


def read_response(name, as_json=True):
	with open(f"scovid19/tests/responses/{name}", "r") as f:
		if as_json:
			return json.loads(f.read())
		return f.read()


class TestInfections:
	@responses.activate
	def test_councils(self):
		responses.add(
			responses.GET,
			"https://www.opendata.nhs.scot/en/api/3/action/datastore_search?resource_id=967937c4-8d67-4f39-974f-fd58c4acfda5",
			json=read_response("councils.json", as_json=True),
			status=200,
		)

		infections = Infections()
		councils = infections.councils()
		assert len(councils.keys()) == 36
