from lib.OpenData import OpenData
from lib.Util import Util
from datetime import datetime
from collections import defaultdict
from lib.Decorators import cacheable
import logging

# TODO: 
# - Confirm @cacheable decorator works
# - Add heavier caching for things that won't change

class SCOVID:
	def __init__(self):
		self._cache = {}

	# Get the mapping of council IDs to council names
	@cacheable
	def councils(self):
		councils = OpenData.fetch('councils')
		return { council['CA']: council['CAName'] for council in councils['records'] }

	# Get the population of each council area for 2019
	@cacheable
	def population(self):
		populations = OpenData.fetch('population', limit=10000)['records']
		return [x for x in populations if x['Year'] == 2019 and x['Sex'] == 'All']

	# Return the summary of stats
	def summary(self):
		cases_by_day = OpenData.fetch('daily', limit=1000, sort='Date ASC')
		records = cases_by_day['records']

		summary = {
			'cases': {
				'total': records[-1]['CumulativeCases'],
				'new': sum([x['DailyCases'] for x in records[-7:]])
			},
			'deaths': {
				'total': records[-1]['Deaths'],
				'new': records[-1]['Deaths'] - records[-7]['Deaths']
			}
		}

		max_deaths = {}
		max_cases = {}
		prev_day = {}
		for day in records:
			new_deaths = day['Deaths'] - prev_day['Deaths'] if prev_day else day['Deaths']

			if not max_deaths or new_deaths > max_deaths['number']:
				max_deaths['number'] = new_deaths
				max_deaths['date'] = Util.strpstrf(day['Date'], strf='%d %b %Y')

			if not max_cases or day['DailyCases'] > max_cases['number']:
				# On Apr 19th the stats started to include UK test centres
				# So this day isn't really an accurate representation
				if day['Date'] != 20200420:
					max_cases['number'] = day['DailyCases']
					max_cases['date']   = Util.strpstrf(day['Date'], strf='%d %b %Y')

			prev_day = day

		summary['cases']['most']  = max_cases
		summary['deaths']['most'] = max_deaths
		return summary

	# Return the overall cases by day for Scotland
	def trend(self, params={}):
		limit, offset = 30, 0

		if 'start' in params and 'end' in params:
			start = datetime.strptime(params['start'], '%Y-%m-%d')
			end = datetime.strptime(params['end'], '%Y-%m-%d')
			last_updated = self.last_updated()

			limit = (end - start).days + 1 # Add one to make bounds inclusive
			offset = (last_updated - end).days
			if offset < 0:
				offset = 0

		trend = OpenData.fetch('daily', sort='Date DESC', limit=limit, offset=offset)
		records = reversed(trend['records'])

		dates = []
		cases = []
		for day in records:
			# On Apr 19th the stats started to include UK test centres
			# So this day isn't really an accurate representation
			if day['Date'] == 20200420:
				day['DailyCases'] = 0

			date = Util.strpstrf(str(day['Date']), strf='%d %b %y')
			dates.append(date)
			cases.append(day['DailyCases'])

		return {
			'labels': dates,
			'datasets': [{
				'backgroundColor': 'darkorange',
				'label': 'Positive',
				'data': cases
			}]
		}

	def breakdown(self):
		positive, negative, deaths = 0, 0, 0

		# There doesn't seem to be a good endpoint for getting total negatives
		# So use total_by_deprivation and total it manually
		total_by_deprivation = OpenData.fetch('total_by_deprivation')
		records = total_by_deprivation['records']
		for record in records:
			positive += record['TotalPositive']
			negative += record['TotalNegative']
			deaths   += record['TotalDeaths']

		return {
			'labels': ['Positive', 'Negative', 'Deaths'],
			'datasets': [{
				'backgroundColor': ['darkorange', 'lightgreen', 'darkgrey'],
				'borderColor': ['darkorange', 'lightgreen', 'darkgrey'],
				'label': 'Breakdown',
				'data': [ positive, negative, deaths ]
			}]
		}

	def locations_total(self):
		total_by_area = OpenData.fetch('total_by_area')
		records = total_by_area['records']

		councils = self.councils()

		sets = []
		for location in records:
			sets.append({
				'x': councils[location['CA']],
				'y': location['TotalCases']
			})

		sets = sorted(sets, key=lambda k: k['x'])
		return {
			'labels': sorted(set(councils.values())),
			'datasets': [{
				'backgroundColor': [ SCOVID.color(item['x']) for item in sets ],
				'label': 'Cases by area',
				'data': sets
			}]
		}

	def locations_new(self):
		councils = self.councils()
		daily_by_area = OpenData.fetch('daily_by_area', limit=(len(councils) * 7), sort='Date DESC')
		records = daily_by_area['records']

		totals = defaultdict(lambda: 0)
		for record in records:
			totals[record['CA']] += record['DailyPositive']

		sets = []
		for ca in totals.keys():
			if not ca or ca not in councils:
				continue

			sets.append({
				'x': councils[ca],
				'y': totals[ca]
			})

		sets = sorted(sets, key=lambda k: k['x'])
		return {
			'labels': sorted(set(councils.values())),
			'datasets': [{
				'backgroundColor': [ SCOVID.color(item['x']) for item in sets ],
				'label': 'Cases by area',
				'data': sets
			}]
		}

	def prevalence(self):
		councils = self.councils()
		populations = self.population()

		total_by_area = OpenData.fetch('total_by_area')['records']
		cases = { x['CA']: x['TotalCases'] for x in total_by_area }

		prevalence = []
		for pop in populations:
			if pop['CA'] not in councils:
				continue
			
			# Work out cases per thousand people
			quotient = pop['AllAges'] / 1000
			per_thousand = cases[pop['CA']] / quotient
			
			prevalence.append({
				'council': councils[pop['CA']],
				'population': format(pop['AllAges'], ','),
				'cases': format(cases[pop['CA']], ','),
				'per_thousand': round(per_thousand, 3)
			})

		return sorted(prevalence, key=lambda x: x['per_thousand'], reverse=True)

	# Get the last updated time of the OpenData stats
	# Based on the latest date in the "Daily and Cumulative Cases" data set
	def last_updated(self, format=None):
		cases_by_day = OpenData.fetch('daily', limit=1, sort='Date DESC')
		records = cases_by_day['records']
		last_updated = datetime.strptime(str(records[-1]['Date']), '%Y%m%d')

		if format:
			return datetime.strftime(last_updated, format)
		
		return last_updated

	@staticmethod
	def color(key):
		key = key.strip()

		color_map = {
			# Types
			'deaths': '#b3b3b3',
			'negative': '#b2df8a',
			'positive': 'ff7f00',

			# Locations
			'Aberdeen City': '#33a02c',
			'Aberdeenshire': '#1f78b4',
			'Angus': '#b2df8a',
			'Argyll and Bute': '#a6cee3',
			'City of Edinburgh': '#fb9a99',
			'Clackmannanshire': '#e31a1c',
			'Dumfries and Galloway': '#fdbf6f',
			'Dundee City': '#ff7f00',
			'East Ayrshire': '#cab2d6',
			'East Dunbartonshire': '#6a3d9a',
			'East Lothian': '#ffff99',
			'East Renfrewshire': '#b15928',
			'Falkirk': '#66c2a5',
			'Fife': '#a6d854',

			# TODO: These need nicer colors
			'Glasgow City': 'orangered',
			'Highland': 'blue',
			'Inverclyde': 'purple',
			'Midlothian': 'cyan',
			'Moray': 'pink',
			'Na h-Eileanan Siar': 'burgandy',
			'North Ayrshire': 'red',
			'North Lanarkshire': 'yellow',
			'Orkney Islands': 'lime',
			'Perth and Kinross': 'rebeccapurple',
			'Renfrewshire': 'brown',
			'Scottish Borders': 'lightblue',
			'Shetland Islands': 'navy',
			'South Ayrshire': 'green',
			'South Lanarkshire': 'orange',
			'Stirling': 'darkgreen',
			'West Dunbartonshire': 'grey',
			'West Lothian': 'magenta',
		}

		return color_map[key] if key in color_map else 'yellow'
