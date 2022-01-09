from flask import request, Blueprint
from app.controllers import Infections, Vaccines
from app.lib.Decorators import endpoint_handler


api = Blueprint("api", __name__)


# Misc
@api.route("/ping")
def ping():
    return "Ok"


# Infections
@api.route("/infections/trend")
@endpoint_handler
def trend():
    infections = Infections()
    return infections.trend(**request.args)


@api.route("/infections/breakdown")
@endpoint_handler
def breakdown():
    infections = Infections()
    return infections.breakdown()


@api.route("/infections/by_age")
@endpoint_handler
def by_age():
    infections = Infections()
    return infections.by_age()


@api.route("/infections/hospital_admissions")
@endpoint_handler
def hospital_admissions():
    infections = Infections()
    return infections.hospital_admissions()


# Vaccines
@api.route("/vaccines/breakdown")
@endpoint_handler
def percentage_vaccinated():
    vaccines = Vaccines()
    return vaccines.percentage()


@api.route("/vaccines/trend")
@endpoint_handler
def vaccine_trend():
    vaccines = Vaccines()
    return vaccines.trend()


@api.route("/prevalence")
@endpoint_handler
def prevalence():
    infections = Infections()
    limit = int(request.args["limit"]) if "limit" in request.args else -1
    return infections.prevalence()[0:limit]
