#!/usr/bin/env python3
import sys
import os
sys.path.append(".")
sys.path.append("%s/src" % os.getcwd())

import pytest
import validators
import logging
import click
import logging
from click.testing import CliRunner

import lib.logger
from lib.logger import logger, info, error, init_logger

## tests ########################################

def setup_module(module):
  trace = "tests#test_logger#setup_module"
  info("Enter", trace, { "module": module, })
  info("Exit", trace)

def teardown_module(module):
  trace = "tests#test_aws#teardown_module"
  info("Enter", trace, { "module": module, })
  info("Exit", trace)

def test_loglevel_info():
  trace = "tests#test_logger#test_loglevel_info"
  info("Enter", trace)

  init_logger("INFO")
  assert logger().getEffectiveLevel() == logging.INFO

  info("Exit", trace)

def test_loglevel_error():
  trace = "tests#test_logger#test_loglevel_info"
  info("Enter", trace)

  init_logger("ERROR")
  assert logger().getEffectiveLevel() == logging.ERROR

  info("Exit", trace)
