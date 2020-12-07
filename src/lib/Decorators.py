import functools
from flask import jsonify, render_template
import logging

# Endpoint decorator
# Try/Except and return JSON
def endpoint(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return jsonify(func(*args, **kwargs))
		except Exception as e:
			logging.error(f"Error when calling endpoint '{func.__name__}': {e}")
			return jsonify({ 'error': 'Something went wrong' })
	
	return wrapper


# Page decorator
# Try/Except and show error.html on error
def page(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			logging.error(f"Error when loading page '{func.__name__}': {e}")
			return render_template('error.html')
	
	return wrapper


# Cacheable decorator
def cacheable(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		this = args[0]
		
		args_key   = [ str(x) for x in args[1:] ]
		kwargs_key = [ f'{k}:{v}' for k,v in kwargs.items() ]
		cache_key  = ';'.join([ func.__name__, *args_key, *kwargs_key ])

		if hasattr(this, '_cache') and cache_key in this._cache:
			return this._cache[cache_key]
		
		result = func(*args, **kwargs)
		this._cache[func.__name__] = result
		return result

	return wrapper

