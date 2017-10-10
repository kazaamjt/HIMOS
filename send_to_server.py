"""
just a util file which will send a measurement to the server - useful when developing the server

just run the file
"""
from requests import post
json = """
{
  "py\/object": "Shared.HardwareObjects.Computer",
  "CPU": [
    {
      "py\/object": "Shared.HardwareObjects.CPU",
      "clock": null,
      "cores": [
        {
          "py\/object": "Shared.HardwareObjects.Core",
          "clock": 2712.256,
          "identifier": "\/intelcpu\/0\/1",
          "load": 5.461639,
          "name": "CPU Core #1",
          "temperature": 36
        },
        {
          "py\/object": "Shared.HardwareObjects.Core",
          "clock": 2712.256,
          "identifier": "\/intelcpu\/0\/2",
          "load": 5.396616,
          "name": "CPU Core #2",
          "temperature": 42
        }
      ],
      "identifier": "\/intelcpu\/0",
      "load": 5.429131,
      "name": "Intel Core i3-6100H",
      "power_package": 7.156284,
      "temperature": 42
    }
  ],
  "GPU": [
    
  ],
  "HDD": [
    {
      "py\/object": "Shared.HardwareObjects.HDD",
      "identifier": "\/hdd\/0",
      "name": "WDC WDS250G1B0B-00AS40",
      "temperature": 49,
      "used_space": 28.93395
    }
  ],
  "Mainboard": "W65_W67RZ1",
  "RAM": [
    {
      "py\/object": "Shared.HardwareObjects.RAM",
      "identifier": "\/ram",
      "name": "Generic Memory",
      "unused_memory": 8.472813,
      "used_memory": 7.416584
    }
  ],
  "hostname": "DESKTOP-SNLE2B%i",
  "time_now_utc": "2017-08-28T07:09:56"
}
"""

server_endpoint = "http://localhost:5000/api/add_measurement"
for host_id in range(1, 20):

	payload = {
		'payload': json % host_id
	}
	response = post(server_endpoint,data=payload)
	assert response.status_code == 200, "Server errored out with %i - %s" % (response.status_code, response.text)

