class HardwareTypes(object):
	MAINBOARD = 0
	SUPER_IO = 1
	CPU = 2
	RAM = 3
	NVIDIA_GPU = 4
	ATI_GPU = 5
	T_BALANCER = 6
	HEATMASTER = 7
	HDD = 8

class SensorTypes(object):
	VOLTAGE = 0
	CLOCK = 1
	TEMPERATURE = 2
	LOAD = 3
	FAN = 4
	FLOW = 5
	CONTROL = 6
	LEVEL = 7
	FACTOR = 8
	POWER = 9
	DATA = 10
	SMALL_DATA = 11
	
	@staticmethod
	def sensor_type_name(sensor_type_id):
		for sensor_type, id in obj_public_attributes(SensorTypes):
			if id == sensor_type_id:
				return sensor_type
