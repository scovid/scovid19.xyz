from flask import render_template, Blueprint
from app.lib.data import Infections, Vaccines
from app.lib.Decorators import page_handler


pages = Blueprint("pages", __name__)


# Page routes
@pages.route("/")
@page_handler
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


@pages.route("/infections")
@page_handler
def index():
    infections = Infections()
    return render_template(
        "infections.html.j2",
        summary=infections.summary(),
        last_updated=infections.last_updated(format="%d %b %y"),
        tab="overview",
    )


@pages.route("/vaccines")
@page_handler
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
