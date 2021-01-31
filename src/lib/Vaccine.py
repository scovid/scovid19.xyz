from lib.SCOVID import SCOVID
from lib.OpenData import OpenData
import logging


class Vaccine(SCOVID):
    def __init__(self):
        self._cache = {}

    def vaccines_weekly(self):
        cases_by_week = OpenData.fetch("weekly_vaccine", limit=1000)
        records = cases_by_week["records"]

        latestrecords = []

        latestweek = records[-1]["WeekEnding"]
        for record in records:
            if record["WeekEnding"] == latestweek:
                latestrecords.append(record)

        councils = self.councils()
        totals = self.get_totals(records)
        weekly = self.get_totals(latestrecords)

        return {
            "this week": {"Dose 1": weekly["dose1"], "Dose 2": weekly["dose2"]},
            "totals": {"Dose 1": totals["dose1"], "Dose 2": totals["dose2"]},
        }

    def get_totals(self, records):
        totals = {
            "dose1": 0,
            "dose2": 0,
        }

        for record in records:
            logging.info(record["Dose"])
            if record["Dose"] == "Dose 1":
                if record["NumberVaccinated"]:
                    totals["dose1"] += record["NumberVaccinated"]
            elif record["Dose"] == "Dose 2":
                if record["NumberVaccinated"]:
                    totals["dose2"] += record["NumberVaccinated"]

        return totals
