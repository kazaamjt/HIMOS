from flask import request, json, session

from Server.app import redis
from Server.app.api_utils import fail_with, reconstruct_computer
from Server.app.measurements_redis_adapter import ComputerMeasurementsRedisAdapter
from Shared.HardwareObjects import Computer
from . import api


@api.route('/newest/<node_identifier>')
def newest(node_identifier):
	newest_entry_json = ComputerMeasurementsRedisAdapter.get_newest_computer_measurement_from_redis(
		node_identifier=node_identifier,
		deserialize=False)

	return newest_entry_json or fail_with("No entries for %s" % node_identifier, 400)


@api.route('/add_measurement', methods=['POST'])
def add_measurement():
	"""
	This is the endpoint that nodes call - they send us their current status in the form of a hardware_objects_lib.Computer
	object. Internally we enqueue each such Computer object for each node that has called this api.
	POST request with form data in the form:
	{
		"payload": <json string of a Computer object>
	}
	:return:
		- on success - http code 200
		- on ignored - http code 202. if the node was marked as one which should be forgotten from the management dashboard
		- on empty input data - http code 400
		- on failure to deserialize the json - http code 500
	"""
	computer_json = request.form.get('payload')
	if not computer_json:
		return fail_with("Empty input data.", 400)

	try:
		# we don't actually need the Computer object now.
		# we just made sure we can deserialize it
		computer = reconstruct_computer(computer_json)
	except Exception as ex:
		return fail_with("Cannot deserialize the input", 500)
	if ComputerMeasurementsRedisAdapter.add_measurement(node_identifier=computer.hostname, computer_json=computer_json):
		return 'ok'
	else:
		return fail_with('measurements for node %s are ignored.' % computer.hostname, code=202)


@api.route('/get_all_measurements/<node_identifier>')
def get_all_measurements(node_identifier):
	# TODO serializing a serialized string
	import json
	return json.dumps(ComputerMeasurementsRedisAdapter.get_all_for_node(node_identifier, deserialize=False))


@api.route('/validate', methods=['POST'])
def validate():
	# helper endpoint to validate jsoned computer.
	computer_json = request.form.get('payload')
	try:
		# we don't actually need the Computer object now.
		# we just made sure we can deserialize it
		computer = reconstruct_computer(computer_json)
		print('validated!')
		return 'ok'
	except Exception as ex:
		return fail_with("Cannot deserialize the input", 500)




@api.route('/ping')
def ping():
	return 'pong'



@api.route('/ping_redis')
def ping_redis():
	try:
		assert redis.ping()
		return 'pong'
	except:
		return fail_with("redis ping failed", 500)
