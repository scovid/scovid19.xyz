from lib.SCOVID import SCOVID
from lib.OpenData import OpenData
from datetime import datetime
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
            "this week": {"Dose 1": weekly["dose1"], "Dose 2": weekly["dose2"], 'Week Ending': datetime.strptime(str(records[-1]['WeekEnding']), '%Y%m%d').strftime('%d/%m/%Y')},
            "totals": {"Dose 1": totals["dose1"], "Dose 2": totals["dose2"]},
        }

    def get_totals(self, records):
        totals = {
            "dose1": 0,
            "dose2": 0,
        }

        for record in records:
            logging.info(record["Dose"])

            # BUG: For some reason the AstraZeneca data has a blank number vaccinated
            if record["NumberVaccinated"].strip() == "":
                continue

            if record["Dose"] == "Dose 1":
                if record["NumberVaccinated"]:
                    totals["dose1"] += int(record["NumberVaccinated"])
            elif record["Dose"] == "Dose 2":
                if record["NumberVaccinated"]:
                    totals["dose2"] += int(record["NumberVaccinated"])

        return totals
