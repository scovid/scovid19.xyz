from lib.SCOVID import SCOVID
from lib.OpenData import OpenData

class Vaccine(SCOVID):
    def __init__(self):
        self._cache = {}

    def vaccines_weekly(self):
        cases_by_week = OpenData.fetch('weekly_vaccine')
        records = cases_by_week['records']

        return records