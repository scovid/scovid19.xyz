from flask import Flask, jsonify, render_template
from lib.SCOVID import SCOVID

app = Flask(__name__, static_url_path='')

# Page routes
@app.route("/")
def index():
	return render_template('index.html',
		summary=SCOVID.summary(),
		last_updated=SCOVID.last_updated()
	)

@app.route("/locations")
def locations():
	return render_template('locations.html')

# API routes
@app.route("/api/trend")
def trend():
	return jsonify(SCOVID.trend())

@app.route("/api/breakdown")
def breakdown():
	return jsonify(SCOVID.breakdown())

@app.route("/api/locations/total")
def locations_total():
	return jsonify(SCOVID.locations_total())

@app.route("/api/locations/new")
def locations_new():
	return jsonify(SCOVID.locations_new())


if __name__ == "__main__":
	app.run()
