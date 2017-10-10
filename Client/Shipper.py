from jsonpickle import encode as json_encode
from requests import post as http_post, get as http_get
from Client.Logger import logger

class Shipper(object):
	"""
	Responsible for sending  hardware_objects_lib.Computer objects
	to the centralized server which handles these data.
	"""

	def __init__(self, host, port, timeout=5):
		self.timeout = timeout
		common_endpoint_format = "http://{host}:{port}/{endpoint}"
		self._server_ship_address = common_endpoint_format.format(
			host=host, port=port,
			endpoint="api/add_measurement"
		)
		self._server_ping_address = common_endpoint_format.format(
			host=host, port=port,
			endpoint="api/ping"
		)
		self._ping_server()

	def _ping_server(self):
		try:
			response = http_get(self._server_ping_address, timeout=self.timeout)
			assert response.status_code == 200 and response.text == 'pong'
		except Exception as ex:
			logger.critical("Pinging the server failed! Shipping will probably fail!")
			logger.critical("Exception msg: [%s]" % str(ex))


	def ship(self, computer_obj):
		try:
			computer_json = json_encode(computer_obj, unpicklable=True)
			payload = {
				'payload': computer_json
			}
			response = http_post(self._server_ship_address, data=payload, timeout=self.timeout)
			if response.status_code == 200:
				pass
			elif response.status_code == 202:
				logger.warning('The server ignored the shipped measurement')
			else:
				logger.warning(
					'Server responded with status code %i and message %s' % (response.status_code, response.text))
		except Exception as ex:
			logger.critical("Cannot ship to the server")
			logger.critical("Exception msg: [%s]" % str(ex))

