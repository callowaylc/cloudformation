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
import boto3
from moto import mock_s3, mock_cloudformation
from click.testing import CliRunner

from fixtures import (
  bucket,
  resource_file,
  path_remote,
  profile,
  template_content,
)

from lib.logger import info, error, init_logger
from lib.util import create_artifact
from lib.aws import (
  s3_push,
  cloudformation_orchestrate,
  cloudfront_distribution,
)

## tests ########################################

def setup_module(module):
  trace = "tests#test_aws#setup_module"
  info("Enter", trace, { "module": module, })
  init_logger()
  info("Exit", trace)

def teardown_module(module):
  trace = "tests#test_aws#teardown_module"
  info("Enter", trace, { "module": module, })

  for f in glob.glob('./build/*'):
    os.remove(f)

  info("Exit", trace)

@mock_s3
def test_s3_push(bucket, resource_file, path_remote):
  trace = "tests#test_aws#test_s3_push"
  info("Enter", trace, {
    "bucket": bucket,
    "resource_file": resource_file,
    "path_remote": path_remote,
  })

  conn = boto3.resource("s3", region_name=os.environ["AWS_DEFAULT_REGION"])
  conn.create_bucket(Bucket=bucket)

  path = create_artifact(resource_file, "hello cloudformation")
  s3_push(bucket, path, path_remote)
  info("Exit", trace)

@mock_cloudformation
def test_cloudformation_orchestrate(profile, template_content):
  trace = "tests#test_aws#test_cloudformation_orchestrate"
  info("Enter", trace, {
    "profile": profile,
    "template_content": template_content,
  })

  cloudformation_orchestrate(profile, DisableBucket=True, Content=template_content)
  info("Exit", trace)
