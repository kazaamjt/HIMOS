import os
import clr
import sys
import platform
from time import sleep

system = platform.system()
if system == "Windows":
	sys.path.append('C:\\Program Files\\HW_Client')
	clr.AddReference('C:\\Program Files\\HW_Client\\OHMlib.dll')
	from OpenHardwareMonitor import Hardware as OPH_Hardware

	import servicemanager
	import win32service  
	import win32serviceutil  
	import win32event
else:
	raise NotImplementedError("Only Windows OS is currently supported for clients")

from Client.Types import *
from Client.Shipper import Shipper
from Client.Config import settings
from Client.Logger import logger
from Shared.HardwareObjects import *
from Shared.Utils import *

logger.setLevel(settings.LogLevel)

class Constructor(object):
	def __init__(self):
		self.OHWM = OPH_Hardware.Computer()
		self.OHWM.CPUEnabled = settings.CPUEnabled
		self.OHWM.RAMEnabled = settings.RAMEnabled
		self.OHWM.GPUEnabled = settings.GPUEnabled
		self.OHWM.HDDEnabled = settings.HDDEnabled
		self.OHWM.MainboardEnabled = settings.MainboardEnabled

		self.OHWM.Open()

	def update(self):
		computer = Computer()
		for hw_item in self.OHWM.Hardware:
			hw_item.Update()

			hardware_type = hw_item.HardwareType

			if hardware_type == HardwareTypes.CPU:
				cpu = self._make_cpu(ohw_cpu=hw_item)
				computer.add_cpu(cpu)

			elif hardware_type == HardwareTypes.HDD:
				hdd = self._make_hdd(hw_item)
				computer.add_hdd(hdd)

			elif hardware_type == HardwareTypes.RAM:
				ram = self._make_ram(hw_item)
				computer.add_ram(ram)

			elif hardware_type == HardwareTypes.MAINBOARD:
				computer.Mainboard = hw_item.Name

		return computer

	def _make_cpu(self, ohw_cpu):
		cpu = CPU(ohw_cpu.Name, ohw_cpu.Identifier.ToString())

		for sensor in ohw_cpu.Sensors:
			sensor_name = sensor.Name
			sensor_value = sensor.Value

			if "CPU Core" in sensor_name:
				pass
			elif "CPU Total" in sensor_name:
				cpu.load = sensor_value
			elif "CPU Package" in sensor_name:
				sensor_type = sensor.SensorType
				if sensor_type == SensorTypes.TEMPERATURE:
					cpu.temperature = sensor_value
				elif sensor_type == SensorTypes.POWER:
					cpu.power_package = sensor_value
				elif sensor_type == SensorTypes.CLOCK:
					cpu.clock = sensor_value
				elif sensor_type == SensorTypes.LOAD:
					cpu.load = sensor_value

		# init the CPU Cores for this CPU and set their sensor measurements
		cpu_cores = self._make_cores(ohw_cpu=ohw_cpu)
		# add all the cores that belong to this CPU to the CPU
		for core in cpu_cores:
			cpu.add_core(core)

		return cpu

	def _make_cores(self, ohw_cpu):
		"""
		Given the sensors of a single CPU, return the Core objects for this CPU
		:param ohw_cpu: OpenHardwareMonitor.Hardware.CPU.<cpu type> object
		:return: list of hardware_objects_lib.Core objects
		"""
		cores_dict = {}  # core name -> Core dictionary
		# traverse all sensors, and if the measurement is for a Core,
		# update the corresponding Core object in `cores`.
		for sensor in ohw_cpu.Sensors:
			sensor_name = sensor.Name
			sensor_value = sensor.Value
			sensor_type = sensor.SensorType

			if is_core_name(sensor_name):
				# either add a new Core object to `cores` or if we've seen  a measurement
				# for this core before, just use the core obj

				if sensor_name not in cores_dict:
					core_id = get_core_identifier(cpu_identifier=ohw_cpu.Identifier.ToString(),
													sensor_identifier=sensor.Identifier.ToString())
					core = Core(name=sensor_name, identifier=core_id)
					cores_dict[sensor_name] = core
				else:
					core = cores_dict[sensor_name]

				if sensor_type == SensorTypes.LOAD:
					core.load = sensor_value
				elif sensor_type == SensorTypes.TEMPERATURE:
					core.temperature = sensor_value
				elif sensor_type == SensorTypes.CLOCK:
					core.clock = sensor_value
				elif sensor_type == SensorTypes.POWER:
					core.power = sensor_value

		return list(cores_dict.values())  # return just a list of the Core objects from the dict

	def _make_hdd(self, ohw_hdd):
		"""
		Extract info from the and build an instance of our HDD class
		:param ohw_hdd:  OHW item - element of self.OHWM.Hardware
		:return: instance of hardware_objects_lib.HDD
		"""
		hdd = HDD(name=ohw_hdd.Name, identifier=ohw_hdd.Identifier.ToString())
		for sensor in ohw_hdd.Sensors:
			if sensor.SensorType == SensorTypes.TEMPERATURE:
				hdd.temperature = sensor.Value
			elif sensor.SensorType == SensorTypes.LOAD:  # Used space
				hdd.used_space = sensor.Value

		return hdd

	def _make_ram(self, ohw_ram):
		"""
		Take the used and available RAM memory statistics and create a hardware_objects_lib.RAM object with them.
		:param ohw_ram:  OHW item - element of self.OHWM.Hardware
		:return:
		"""
		ram = RAM(name=ohw_ram.Name, identifier=ohw_ram.Identifier.ToString())

		for sensor in ohw_ram.Sensors:
			sensor_type = sensor.SensorType
			sensor_value = sensor.Value
			sensor_name = sensor.Name

			if sensor_type == SensorTypes.LOAD:
				pass
			elif sensor_type == SensorTypes.DATA:
				if "used memory" in sensor_name.lower():
					ram.used_memory = sensor_value
				elif "available memory" in sensor_name.lower():
					ram.unused_memory = sensor_value

		return ram

# Init the constructor and the shipper
constructor = Constructor()
shipper = Shipper(settings.server_address,
					settings.server_port,
					settings.http_timeout)

def run():
	while True:
		computer = constructor.update()
		shipper.ship(computer)
		sleep(settings.refresh_interval)

def send_once():
	computer = constructor.update()
	shipper.ship(computer)

class win_service(win32serviceutil.ServiceFramework):
	_svc_name_ = "HW_Client_Service"
	_svc_display_name_ = "Hardware Monitor Client Service"
	_svc_description_ = "Collects hardware stats and ships them to a server"

	def __init__(self, args):  
		win32serviceutil.ServiceFramework.__init__(self,args)  
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)  

	# core logic of the service     
	def SvcDoRun(self):
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		# inti extra stuff here if needed
		rc = None  
		
		# Set status to running
		self.ReportServiceStatus(win32service.SERVICE_RUNNING)

		# if the stop event hasn't been fired keep looping
		i = settings.refresh_interval
		while rc != win32event.WAIT_OBJECT_0:  
			if i == settings.refresh_interval:
				send_once()
				i = 0
			rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
			i += 1

		self.stop()

	def SvcStop(self):  
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)  
		win32event.SetEvent(self.hWaitStop)

	def stop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
	if system == "Windows":
		if len(sys.argv) == 1:
			servicemanager.Initialize()
			servicemanager.PrepareToHostSingle(win_service)
			servicemanager.StartServiceCtrlDispatcher()
		else:
			win32serviceutil.HandleCommandLine(win_service)

	else:
		run()
