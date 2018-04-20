#!/usr/bin/env python3
import sys
import os
sys.path.append(".")
sys.path.append("%s/src" % os.getcwd())

import pytest
import json
from jinja2 import Template
from click.testing import CliRunner
from click import Context, Command
from lib.logger import info, error

## general ######################################

@pytest.fixture
def envs():
  return [
    "AWS_SESSION_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "AWS_CLOUDFORMATION_BUCKET_NAME",
    "AWS_CLOUDFORMATION_BUCKET_DOMAIN",
    "AWS_LAMBDA_BUCKET_NAME",
    "BUCKET",
    "WORKDIR",
  ]

## test_runner.py ###############################

@pytest.fixture
def template():
  return Template("hello {{ Stack }}!")

@pytest.fixture
def profile():
  return {
    "Stack": "StackName",
    "Template": "s3.yaml",
    "Region": "us-east-1",
    "Inputs": {
      "Name": "Stack",
    }
  }


@pytest.fixture
def args():
  return [
    "--disable-rollback",
    "test.py",
  ]

## test_cloudformation.py ################################

@pytest.fixture(scope="module")
def runner():
  return CliRunner()

@pytest.fixture(scope="module")
def runner_flags():
  return [ "--help" ]

## test_util.py #################################

@pytest.fixture(scope="module")
def resource_file():
  return "test.user.yaml"


@pytest.fixture(scope="module")
def resource_paths():
  return "./profiles:./build"

## test_aws.py ##################################

@pytest.fixture(scope="module")
def bucket():
  return os.environ["AWS_CLOUDFORMATION_BUCKET_NAME"]

@pytest.fixture(scope="module")
def path_remote():
  return "/tests/test.yaml"

@pytest.fixture(scope="module")
def template_content():
  with open("./templates/user.yaml", "r") as f:
    return f.read()

## test_cloudformation.py #######################

@pytest.fixture(scope="module")
def main_arguments():
  return [
    "--dry",
    "--loglevel", "INFO",
    "--help",
  ]

@pytest.fixture(scope="module")
def cloudformation_arguments():
  return [
    "--dry",
    "--loglevel", "INFO",
    "--profile", "test.yaml",
      "cloudformation", "--help"
  ]

