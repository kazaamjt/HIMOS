import configparser
from Client.Logger import logger

class Settings(object):
	def __init__(self):
		self._config = configparser.ConfigParser()
		self._config.read('C:\\Program Files\\HW_Client\\Client.ini')

		# General
		self._general_settings = self._config['General']
		self.refresh_interval = int(self._general_settings['refresh_interval'])

		# Monitor
		self._monitor_list = {'CPU':True, 'RAM':True, 'GPU':True,
							  'HDD':True, 'Mainboard':True}
		for key in self._monitor_list:
			try:
				value = self._config.getboolean('Monitor', key)
			except:
				pass

			if key == 'CPU':
				self.CPUEnabled = value

			elif key == 'RAM':
				self.RAMEnabled = value

			elif key == 'GPU': 
				self.GPUEnabled = value

			elif key == 'HDD':
				self.HDDEnabled = value

			elif key == 'Mainboard':
				self.MainboardEnabled = value

		# Server
		self._server_settings = self._config['Server']
		self.server_address = self._server_settings['Address']
		self.server_port = int(self._server_settings['Port'])

		# Logging
		self._log_dict = {'CRITICAL': 50, 'ERROR': 40,
						  'WARNING': 30, 'INFO': 20,
						  'DEBUG': 10, 'NOTSET': 0}

		self._log_settings = self._config['Logging']
		self.LogLevel = self._log_dict[self._log_settings['Level']]

		# misc
		self._misc_settings = self._config['misc']
		self.http_timeout = int(self._misc_settings['http_timeout'])

settings = Settings()
