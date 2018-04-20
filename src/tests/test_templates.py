#!/usr/bin/env python3
import sys
import os
sys.path.append(".")
sys.path.append("%s/src" % os.getcwd())

import pytest
from pathlib import Path

from lib.logger import logger, info, error, init_logger

## tests ########################################

def setup_module(module):
  trace = "tests#test_templates#setup_module"
  info("Enter", trace, { "module": module, })
  init_logger()
  info("Exit", trace)

def teardown_module(module):
  trace = "tests#test_templates#teardown_module"
  info("Enter", trace, { "module": module, })
  info("Exit", trace)

@pytest.mark.parametrize("path, glob", [( "./templates" ,"./*.yaml" )])
def test_yaml(path, glob):
  """Tests yaml correctness of all *.yaml files in templates directory
  """
  trace = "tests#test_templates#test_yaml"
  info("Enter", trace, { "path": path, "glob": glob, })
  info("Exit", trace)

  pathlist = Path(path).glob(glob)
  for p in pathlist:
    info("Examining template", trace, { "path": p, })
    status = os.system("""
      aws cloudformation validate-template --template-body file://%s
    """ % str(p))

    assert status == 0
