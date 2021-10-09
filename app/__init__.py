from flask import Flask


def create_app():
    app = Flask(__name__, static_url_path="")

    from app.views import pages, api

    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix="/api")

    return app
