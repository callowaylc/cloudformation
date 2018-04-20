#!/usr/bin/env python3
import sys
import os
sys.path.append(".")
sys.path.append("%s/src" % os.getcwd())

import pytest
import validators
import yaml
import logging
import click
import glob
from click.testing import CliRunner

from lib.util import create_artifact, resource_path, resource_content
from lib.logger import info, error, init_logger
from fixtures import resource_file, resource_paths

## tests ########################################

def setup_module(module):
  trace = "tests#test_util#setup_module"
  info("Enter", trace, { "module": module, })
  init_logger()
  info("Exit", trace)

def teardown_module(module):
  trace = "tests#test_util#teardown_module"
  info("Enter", trace, { "module": module, })

  for f in glob.glob('./build/*'):
    os.remove(f)

  info("Exit", trace)


@pytest.mark.parametrize("content", [( "hello cloudformation" )])
def test_create_artifact(resource_file, content):
  trace = "tests#test_util#test_create_artifact"
  info("Enter", trace, { "resource_file": resource_file, "content": content, })

  path = create_artifact(resource_file, content)
  assert os.path.isfile(path)

  info("Exit", trace)

@pytest.mark.parametrize("context", [(
  { "name": "cloudformation"}
)])
def test_resource_content(resource_file, resource_paths, context):
  trace = "tests#test_util#test_resource_content"
  info("Enter", trace, {
    "resource_file": resource_file,
    "resource_paths": resource_paths,
    "context": context,
  })

  resource = yaml.load(resource_content(resource_file, resource_paths, context))
  assert "Inputs" in resource
  assert "Name" in resource["Inputs"]
  assert resource["Inputs"]["Name"] == "cloudformation"
  info("Exit", trace)

def test_resource_path(resource_file, resource_paths):
  trace = "tests#test_util#test_resource_path"
  info("Enter", trace, {
    "resource_file": resource_file,
    "resource_paths": resource_paths,
  })

  path = resource_path(resource_file, resource_paths)
  assert os.path.isfile(path)
  info("Exit", trace)
