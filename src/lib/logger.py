#!/usr/bin/env python3
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger
from functools import lru_cache
from importlib import reload

def logger():
  """Returns instance of logger
  """
  return logging.getLogger()

def init_logger(level="INFO"):
  """Return logger instance.

  Instantiates and memoizes logger instance.
  """
  logging.shutdown()
  reload(logging)

  logger = logging.getLogger()
  handler = logging.StreamHandler()
  handler.setFormatter(jsonlogger.JsonFormatter())
  logger.addHandler(handler)
  logger.setLevel(getattr(logging, level))

def info(message, trace, attributes={ }):
  """Log to INFO.
  """
  __log__("info", message, trace, attributes)

def error(message, trace, attributes={ }):
  """Log to ERROR.
  """
  __log__("error", message, trace, attributes)

def __log__(level, message, trace, attributes={ }):
  """Log to DEBUG.

  Logs message and attributes as json to DEBUG level.
  """
  method = getattr(logging.getLogger(), level)
  method(
    {**{ "message": message, "time": str(datetime.now()), "trace": trace }, **attributes}
  )
