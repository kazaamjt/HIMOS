import configparser
from Server.Logger import logger

_config = configparser.ConfigParser()
_config.read('Server.ini')
_misc_settings = _config['misc']
_redis_settings = _config['Redis']


class Settings(object):
	# General
	_general_settings = _config['General']
	Address = _general_settings['Address']
	Port = int(_general_settings['Port'])
	Run_Level = _general_settings['Run_Level'].lower()

	# Logging
	_log_dict = {'CRITICAL': 50, 'ERROR': 40,
				 'WARNING': 30, 'INFO': 20,
				 'DEBUG': 10, 'NOTSET': 0}

	_log_settings = _config['Logging']
	LogLevel = _log_dict[_log_settings['Level']]


class BaseConfig(object):
	# how many log entries from a node we would keep
	MAX_ENTRIES_PER_NODE = int(_misc_settings['Max_Entries_Per_Node'])

	# if a node doesn't report to us within this number of seconds we mark it as dead
	NODE_GONE_AFTER = int(_misc_settings['Consider_Node_Gone_After_Seconds'])

	REDIS_HOST = _redis_settings['Redis_Host']
	REDIS_PORT = _redis_settings['Redis_Port']
	REDIS_DB = _redis_settings['Redis_Db']

	SITE_NAME = _misc_settings['Dashboard_Name']

	SECRET_KEY = 'not that secret'
	DEBUG = _misc_settings['Debug']

	@classmethod
	def init_app(cls, app):
		assert BaseConfig.MAX_ENTRIES_PER_NODE >= 1, "We keep at least one measurement."


class DevelopmentConfig(BaseConfig):
	DEBUG = True

	@classmethod
	def init_app(cls, app):
		super(DevelopmentConfig, cls).init_app(app)


class ProductionConfig(BaseConfig):
	@classmethod
	def init_app(cls, app):
		super(ProductionConfig, cls).init_app(app)


class EnvironmentName:
	"""
	use this class to refer to names of environments to ensure you don't mistype a string
	"""
	development = 'development'
	production = 'production'


settings = Settings()
flask_settings = {
	EnvironmentName.development: DevelopmentConfig,
	EnvironmentName.production: ProductionConfig,
}
