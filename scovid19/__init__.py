from flask import Flask, render_template, request

# Load .env
from dotenv import load_dotenv

load_dotenv()

import os, logging
from scovid19.lib.data import Infections, Vaccines
from scovid19.lib.Decorators import page, endpoint
from scovid19.lib.Util import project_root, get_logger

app = Flask(__name__, static_url_path="")

# Set up logger
app_logger = get_logger("app")

infections = Infections()
vaccines = Vaccines()

# Page routes
@app.route("/")
@page
def dashboard():
	return render_template(
		"dashboard.html.j2",
		infections=infections.summary(),
		vaccines=vaccines.vaccines_weekly(),
		last_updated=infections.last_updated(format="%d %b %y"),
		tab="dashboard",
	)


@app.route("/infections")
@page
def index():
	return render_template(
		"infections.html.j2",
		summary=infections.summary(),
		last_updated=infections.last_updated(format="%d %b %y"),
		tab="overview",
	)


@app.route("/vaccines")
@page
def vaccine():
	return render_template(
		"vaccine.html.j2",
		tab="vaccine",
		weekly=vaccines.vaccines_weekly(),
		percentage=vaccines.percentage_vaccinated(),
		last_updated=infections.last_updated(format="%d %B %Y"),
	)


# == API routes ==#

# Misc
@app.route("/api/ping")
def ping():
	return "Ok"


# Infections
@app.route("/api/infections/trend")
@endpoint
def trend():
	return infections.trend(request.args)


@app.route("/api/infections/breakdown")
@endpoint
def breakdown():
	return infections.breakdown()


@app.route("/api/infections/locations")
@endpoint
def locations():
	full = request.args.get("full", False)
	return infections.locations(full)


# Vaccines
@app.route("/api/vaccines/breakdown")
@endpoint
def percentage_vaccinated():
	return vaccines.percentage_vaccinated()


@app.route("/api/vaccines/council")
@endpoint
def council_breakdown():
	return vaccines.council_breakdown()


@app.route("/api/vaccines/trend")
@endpoint
def vaccine_trend():
	return vaccines.vaccine_trend()


@app.route("/api/prevalence")
@endpoint
def prevalence():
	limit = int(request.args["limit"]) if "limit" in request.args else -1
	return infections.prevalence()[0:limit]


if __name__ == "__main__":
	app.run()
