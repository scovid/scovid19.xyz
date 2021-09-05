from flask import Flask

# Load .env
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(__name__, static_url_path="")

    from app.views import pages, api

    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix="/api")

    return app
