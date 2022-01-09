"""
Tests for scovid19.lib.data using pytest
"""

from app.controllers import Scotland, Infections, Vaccines


class TestScotland:
    def test_councils(self):
        scotland = Scotland()
        councils = scotland.councils()
        assert len(councils.keys()) == 36


class TestVaccines:
    def test_summary(self):
        vaccines = Vaccines()
        results = vaccines.summary()
        assert "this week" in results
        assert "totals" in results
        assert results["this week"]["Dose 1"] > 0
        assert results["this week"]["Dose 2"] > 0
        assert results["totals"]["Dose 1"] > 0
        assert results["totals"]["Dose 2"] > 0


class TestInfections:
    def test_summary(self):
        infections = Infections()
        results = infections.summary()
        assert "cases" in results
        assert "deaths" in results
