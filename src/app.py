from flask import Flask, render_template, request
import logging
from lib.SCOVID import SCOVID
from lib.Decorators import page, endpoint


app = Flask(__name__, static_url_path='')
logging.basicConfig(
	filename='app.log',
	level=logging.INFO,
	format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
)

scovid = SCOVID()

# Page routes
@app.route('/')
@page
def index():
	return render_template('index.html',
		summary=scovid.summary(),
		last_updated=scovid.last_updated(format='%d %B %Y'),
		tab="overview"
	)

@app.route('/vaccine')
@page
def vaccine():
	return render_template('vaccine.html',
		tab="vaccine",
		last_updated=scovid.last_updated(format='%d %B %Y'),
	)

@app.route('/locations')
@page
def locations():
	return render_template('locations.html')


# API routes
@app.route('/api/trend')
@endpoint
def trend():
	return scovid.trend(request.args)


@app.route('/api/breakdown')
@endpoint
def breakdown():
	return scovid.breakdown()


@app.route('/api/locations/total')
@endpoint
def locations_total():
	return scovid.locations_total()


@app.route('/api/locations/new')
@endpoint
def locations_new():
	return scovid.locations_new()


@app.route('/api/prevalence')
@endpoint
def prevalence():
	limit = int(request.args['limit']) if 'limit' in request.args else -1
	return scovid.prevalence()[0:limit]


if __name__ == '__main__':
	app.run()
