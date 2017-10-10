from datetime import datetime
import re

def get_core_identifier(cpu_identifier, sensor_identifier):
    """
    a cpu has many sensors. some of them for cores. cores themselves don't have identifiers.
    thus, we use the identifier of the sensor to infer to which core it belongs.

    :param cpu_identifier: e.g.  /intelcpu/0
    :param sensor_identifier: e.g. /intelcpu/0/load/1  - i.e. the load sensor for core #1 of CPU #0.
    :return: a core identifier e.g. /intelcpu/0/1
    """

    core_number = sensor_identifier.split('/')[-1]
    return cpu_identifier + "/" + core_number

cpu_core_name_regex = re.compile("CPU Core #(\d)")
def is_core_name(test_string):
    """
    is_core_name("CPU Core #1") -> True
    """
    return True if cpu_core_name_regex.match(test_string) else False

