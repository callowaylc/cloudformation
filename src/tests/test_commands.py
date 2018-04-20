#!/usr/bin/env python3
import sys
import os
sys.path.append(".")
sys.path.append("%s/src" % os.getcwd())

import pytest
import validators
import logging
import click
import glob
from click.testing import CliRunner
import boto3
from moto import mock_s3, mock_cloudformation

from lib.logger import info, error, init_logger
from fixtures import (
  envs,
  runner,
  main_arguments,
  cloudformation_arguments,
)

import cloudformation
import commands.main
import commands.cloudformation

## tests ########################################


def setup_module(module):
  trace = "tests#test_commands#setup_module"
  info("Enter", trace, { "module": module, })
  init_logger()
  info("Exit", trace)

def teardown_module(module):
  trace = "tests#test_commands#teardown_module"
  info("Enter", trace, { "module": module, })

  for f in glob.glob('./build/*'):
    os.remove(f)

  info("Exit", trace)

def test_envs(envs):
  trace = "tests#test_commands#test_envs"
  info("Enter", trace, { "envs": envs, })

  for k in envs:
    assert k in os.environ

  info("Exit", trace)

def test_main(runner, main_arguments):
  trace = "tests#test_commands#test_main"
  info("Enter", trace, { "runner": runner, "main_arguments": main_arguments })

  result = runner.invoke(cloudformation.main, main_arguments)
  assert result.exit_code == 0

  info("Exit", trace)

@mock_s3
@mock_cloudformation
def test_cloudformation(runner, cloudformation_arguments):
  trace = "tests#test_commands#test_cloudformation"
  info("Enter", trace, {
    "runner": runner,
    "cloudformation_arguments": cloudformation_arguments,
  })

  result = runner.invoke(cloudformation.cloudformation, [ "--help" ])
  assert result.exit_code == 0

  result = runner.invoke(cloudformation.main, cloudformation_arguments, obj={ })
  assert result.exit_code == 0

  info("Exit", trace)
