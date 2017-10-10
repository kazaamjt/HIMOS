from flask import make_response
import json
from jsonpickle import decode as json_decode

from Shared.HardwareObjects import Computer


def fail_with(msg, code=500):
    msg = {
        'error': msg
    }
    return make_response(json.dumps(msg), code)


def reconstruct_computer(serialized_computer):
    """
    :param serialized_computer: string in json format
    :return:  shared.hardware_objects_lib.Computer object
    """
    computer = json_decode(serialized_computer)
    assert computer.__class__.__name__ == Computer.__name__
    return computer
