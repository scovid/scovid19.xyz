from flask import Flask, jsonify, render_template, request
import logging
from lib.SCOVID import SCOVID
from lib.Decorators import page, endpoint

app = Flask(__name__, static_url_path='')
logging.basicConfig(
	filename='app.log',
	level=logging.INFO,
	format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
)

# Page routes
@app.route('/')
@page
def index():
	return render_template('index.html',
		summary=SCOVID.summary(),
		last_updated=SCOVID.last_updated(format='%Y-%m-%d')
	)

@app.route('/locations')
@page
def locations():
	return render_template('locations.html')


# API routes
@app.route('/api/trend')
@endpoint
def trend():
	return SCOVID.trend(request.args)

@app.route('/api/breakdown')
@endpoint
def breakdown():
	return SCOVID.breakdown()

@app.route('/api/locations/total')
@endpoint
def locations_total():
	return SCOVID.locations_total()

@app.route('/api/locations/new')
@endpoint
def locations_new():
	return SCOVID.locations_new()


if __name__ == '__main__':
	app.run()
