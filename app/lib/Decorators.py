import functools
import logging
import traceback

from app.lib.Cache import Cacher
from flask import jsonify, render_template


# Endpoint decorator
# Try/Except and return JSON
def endpoint_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return jsonify(func(*args, **kwargs))
        except Exception:
            err = traceback.format_exc()
            logging.error(f"Error when calling endpoint '{func.__name__}': {err}")
            return jsonify({"error": "Unknown Error"})

    return wrapper


# Page decorator
# Try/Except and show error.html on error
def page_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            err = traceback.format_exc()
            logging.error(f"Error when loading page '{func.__name__}': {err}")
            return render_template("error.html.j2")

    return wrapper


# Cacheable decorator
def cacheable(og_func=None, cacher=Cacher.default()):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cacher.cache(func, *args, **kwargs)

        return wrapper

    if og_func:
        return decorate(og_func)

    return decorate
