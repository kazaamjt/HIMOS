import socket
from datetime import datetime

class Computer(object):
	def __init__(self):
		self.hostname = socket.gethostname()
		self.time_now_utc = datetime.utcnow().replace(microsecond=0).isoformat()
		self.CPU = []
		self.GPU = []
		self.HDD = []
		self.RAM = []
		self.Mainboard = ""

	def add_cpu(self, cpu_obj):
		"""
		:param
		cpu_obj: hardware_objects_lib.CPU
		object
		"""
		self.CPU.append(cpu_obj)

	def add_gpu(self, gpu_obj):
		"""
		:param
		gpu_obj: hardware_objects_lib.GPU
		object
		"""
		self.GPU.append(gpu_obj)

	def add_hdd(self, hdd_obj):
		"""
		:param
		hdd_obj: hardware_objects_lib.GPU
		object
		"""
		self.HDD.append(hdd_obj)

	def add_ram(self, ram_obj):
		"""
		:param
		hdd_obj: hardware_objects_lib.RAM
		object
		"""
		self.RAM.append(ram_obj)


class HardwareComponent():
	def __init__(self, name, identifier):
		self.name = name
		self.identifier = identifier

	def __repr__(self):
		return '%s (identifier: %s)' % (self.name, self.identifier)

class CPU(HardwareComponent):
	def __init__(self, name, identifier,
			load=None, temperature=None,
			clock=None, power_package=None):
		super(CPU, self).__init__(name, identifier)
		
		self.load = load
		self.temperature = temperature
		self.clock = clock
		self.power_package = power_package
		self.cores = []
		
	def add_core(self, core_obj):
		self.cores.append(core_obj)

class Core(HardwareComponent):
	def __init__(self, name, identifier,
					load=0, temperature=0, clock=0):
		super(Core, self).__init__(name, identifier)
		
		self.load = load
		self.temperature = temperature
		self.clock = clock
	
class HDD(HardwareComponent):
	def __init__(self, name, identifier,
					temperature=None, used_space=None):
		super(HDD, self).__init__(name, identifier)
		self.name = name
		self.identifier = identifier
		self.temperature = temperature
		self.used_space = used_space  # percentage

class RAM(HardwareComponent):
	def __init__(self, name, identifier, used_memory=None, unused_memory=None):
		super(RAM, self).__init__(name, identifier)
		
		self.used_memory = used_memory # in gb
		self.unused_memory = unused_memory # in gb
