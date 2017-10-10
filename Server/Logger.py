import logging

_logger_name = 'HardwareMonitor'
logger = logging.getLogger(_logger_name)
_logger_format = '%(asctime)s %(filename)s:%(module)s %(levelname)s:%(name)s %(message)s'
_formatter = logging.Formatter(_logger_format)
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
