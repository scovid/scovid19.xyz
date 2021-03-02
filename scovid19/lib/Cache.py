import json
import os.path
from time import time
from enum import Enum
from typing import Any
from dataclasses import dataclass, field
from scovid19.lib.Util import project_root, env, get_logger


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


@dataclass
class Cacher:
	"""
	Cache configuration and functions
	"""

	system: System
	valid_for: int  # Seconds cache is valid for
	store: dict[str, Any] = field(default_factory=dict)

	@classmethod
	def default(cls):
		"""
		Default cache configuration
		A class instance cacher, valid for 2 hours
		"""
		return cls(system=System.OBJECT, valid_for=Duration.hours(2))

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
		cache_key = Cacher._make_key(func.__name__, *args, **kwargs)

		if cache_key in self.store:
			cached = self.store[cache_key]
			if cached.get("expires", 0) > time():
				return cached.get("value")

		result = func(*args, **kwargs)
		cached = {"value": result, "expires": time() + self.valid_for}
		self.store[cache_key] = cached
		return result

	# Cache in file
	def file_cache(self, func, *args, **kwargs):
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
		# Ignore 'self' params for our classes
		if (
			len(args) > 0
			and isinstance(args[0], object)
			and args[0].__class__.__module__ != "builtins"
		):
			args = [args[0].__class__.__name__, *args[1:]]

		args_key = [str(x) for x in args]
		kwargs_key = [f"{k}:{v}" for k, v in kwargs.items()]
		return ";".join([name, *args_key, *kwargs_key])
