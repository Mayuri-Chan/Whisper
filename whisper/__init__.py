import os

try:
	import tomllib
except ImportError:
	import tomli as tomllib

config_path = "config.toml"
if not os.path.isfile(config_path):
	CONFIG = None
else:
	with open(config_path, 'rb') as f:
		CONFIG = tomllib.load(f)
