import json
import os.path
from time import time
from enum import Enum
from typing import Any
from dataclasses import dataclass
from scovid19.lib.Util import project_root, env


class CacheException(Exception):
	pass


class System(Enum):
	"""
	Caching methods
	"""

	OBJECT = 1
	FILE = 2


class Duration:
	"""
	Cache duration
	"""

	@staticmethod
	def seconds(num):
		return num

	@staticmethod
	def minutes(num):
		return num * 60

	@staticmethod
	def hours(num):
		return num * 60 * 60

	@staticmethod
	def days(num):
		return num * 24 * 60 * 60


"""
Cache configuration and functions
"""


@dataclass
class Cacher:
	system: System
	valid_for: int  # Seconds cache is valid for
	is_method: bool = False

	@classmethod
	def default(cls):
		"""
		Default cache configuration
		A class instance cacher, valid for 2 hours
		"""
		return cls(system=System.OBJECT, valid_for=Duration.hours(2), is_method=True)

	def cache(self, func, *args, **kwargs):
		"""
		Wrapper that calls the appropriate cache function
		"""
		# Only use cache on prod
		if env() != "prod":
			return func(*args, **kwargs)

		if self.system == System.OBJECT:
			return self.object_cache(func, *args, **kwargs)

		if self.system == System.FILE:
			return self.file_cache(func, *args, **kwargs)

	# Cache in object instance
	def object_cache(self, func, *args, **kwargs):
		if not self.is_method:
			raise CacheException("Can only create object_cache for methods")

		this = args[0]
		actual_args = args[1:] if len(args) > 1 else []
		cache_key = Cacher._make_key(func.__name__, *actual_args, **kwargs)

		if hasattr(this, "_cache") and cache_key in this._cache:
			cached = this._cache[cache_key]
			if cached.get("expires", 0) > time():
				return cached.get("value")

		result = func(*args, **kwargs)
		cached = {"value": result, "expires": time() + self.valid_for}
		this._cache[func.__name__] = cached
		return result

	# Cache in file
	def file_cache(self, func, *args, **kwargs):
		cache_key = None

		# Handle `self`
		if self.is_method:
			actual_args = args[1:] if len(args) > 1 else []
			cache_key = Cacher._make_key(func.__name__, *actual_args, **kwargs)
		else:
			cache_key = Cacher._make_key(func.__name__, *args, **kwargs)

		cache_file = f"{project_root()}/cache/{cache_key}"

		if os.path.isfile(cache_file):
			with open(cache_file, "r") as cache_reader:
				cached = json.loads(cache_reader.read())
				if cached.get("expires", 0) > time():
					return cached.get("value")

		result = func(*args, **kwargs)
		cached = {"value": result, "expires": time() + self.valid_for}

		with open(cache_file, "w") as cache_writer:
			cache_writer.write(json.dumps(cached))

		return result

	@staticmethod
	def _make_key(name, *args, **kwargs):
		"""
		Create a cache key from a func name and it's args
		"""
		args_key = [str(x) for x in args]
		kwargs_key = [f"{k}:{v}" for k, v in kwargs.items()]
		return ";".join([name, *args_key, *kwargs_key])
