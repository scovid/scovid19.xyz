from flask import Flask, render_template, request

# Load .env
from dotenv import load_dotenv

load_dotenv()

from scovid19.lib.data import Infections, Vaccines
from scovid19.lib.Decorators import page, endpoint
from scovid19.lib.Util import get_logger

app = Flask(__name__, static_url_path="")

# Set up logger
app_logger = get_logger("app")


# Page routes
@app.route("/")
@page
def dashboard():
    infections = Infections()
    vaccines = Vaccines()

    return render_template(
        "dashboard.html.j2",
        infections=infections.summary(),
        vaccines=vaccines.summary(),
        last_updated=infections.last_updated(format="%d %b %y"),
        tab="dashboard",
    )


@app.route("/infections")
@page
def index():
    infections = Infections()
    return render_template(
        "infections.html.j2",
        summary=infections.summary(),
        last_updated=infections.last_updated(format="%d %b %y"),
        tab="overview",
    )


@app.route("/vaccines")
@page
def vaccine():
    infections = Infections()
    vaccines = Vaccines()
    return render_template(
        "vaccine.html.j2",
        tab="vaccine",
        weekly=vaccines.summary(),
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
    infections = Infections()
    return infections.trend(request.args)


@app.route("/api/infections/breakdown")
@endpoint
def breakdown():
    infections = Infections()
    return infections.breakdown()


# Vaccines
@app.route("/api/vaccines/breakdown")
@endpoint
def percentage_vaccinated():
    vaccines = Vaccines()
    return vaccines.percentage_vaccinated()


@app.route("/api/vaccines/council")
@endpoint
def council_breakdown():
    vaccines = Vaccines()
    return vaccines.council_breakdown()


@app.route("/api/vaccines/trend")
@endpoint
def vaccine_trend():
    vaccines = Vaccines()
    return vaccines.vaccine_trend()


@app.route("/api/prevalence")
@endpoint
def prevalence():
    infections = Infections()
    limit = int(request.args["limit"]) if "limit" in request.args else -1
    return infections.prevalence()[0:limit]


if __name__ == "__main__":
    app.run()
