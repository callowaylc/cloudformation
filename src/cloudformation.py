#!/usr/bin/env python3
# # -*- coding: utf-8 -*-

"""Provides CLI To Update cloudformation Resources

Usage: cloudformation.py [OPTIONS] COMMAND [ARGS]...

Options:
  --loglevel [DEBUG|INFO|WARNING|ERROR]
  --help                          Show this message and exit.

Commands:
  cloudformation  Orchestrates AWS Cloudformation Profiles
  securitygroup   Orchestrates AWS Security Group Profiles
  waf             Manages A Cloudfront Distribution's WAF IPSet
"""

## imports ######################################

import sys
import logging
import yaml
import traceback
import os.path
import click
import re
from lib.logger import info, error
from datetime import datetime
from functools import lru_cache
from pythonjsonlogger import jsonlogger
from box import Box
from jinja2 import Template

import commands.securitygroup
import commands.waf
import commands.cloudformation
import commands.main

from lib.util import resource_content, create_artifact, responds
from lib.logger import info, error, init_logger

## constants ####################################

SUCCESS = 0
FAILURE = 1

## functions ####################################

@click.group()
@click.option(
  "--loglevel",
  default="ERROR",
  type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
@click.option('--profile', required=True, help='Use a preconfigured profile.')
@click.option('--dry', is_flag=True, help='Disables all mutative actions.')
@click.pass_context
def main(ctx, loglevel, profile, dry):
  trace = "cloudformation#main"
  info("Enter", trace, {
    "ctx": ctx.obj,
    "loglevel": loglevel,
    "profile": profile,
    "dry": dry,
  })

  commands.main.command(ctx, loglevel, profile, dry)

  info("Exit", trace)

@main.command()
@click.option("--timeout", default=10, help="Time to wait for stack completion in minutes")
@click.option(
  "--disable-rollback",
  is_flag=True,
  help="Disables rollback of stack",
)
@click.option(
  "--disable-bucket",
  is_flag=True,
  help="Disables use of s3 bucket for orchestrating templates",
)
@click.option(
  "--capabilities",
  is_flag=True,
  help="Allow Cloudformation Escalated Permissions When Creating IAM Resources",
)
@click.option('--sets', multiple=True, help='Sets a profile value.')
@click.pass_context
def cloudformation(ctx, timeout, disable_rollback, disable_bucket, capabilities, sets):
  """Orchestrates AWS Cloudformation Profiles
  """
  trace = "cloudformation#cloudformation"
  info("Enter", trace, {
   "ctx": ctx.obj,
   "timeout": timeout,
   "disable_rollback": disable_rollback,
   "disable_bucket": disable_bucket,
   "capabilities": capabilities,
   "sets": sets,
  })
  commands.cloudformation.command(
    ctx, timeout, disable_rollback, disable_bucket, capabilities, sets
  )
  info("Exit", trace)

@main.command()
@click.option("--name", required=True, help="Name of security group.")
@click.option("--add", multiple=True, help="Add rule.")
@click.option("--remove", help="Remove rule(s) by regular expression.")
@click.option(
  "--ingress",
  "direction",
  required=True,
  flag_value="ingress",
  help="Ops against ingress rules only."
)
@click.option(
  "--egress",
  "direction",
  required=True,
  flag_value="egress",
  help="Ops against egress rules only."
)
@click.pass_context
def securitygroup(ctx, name, add, remove, direction):
  """Orchestrates AWS Security Group Profiles
  """
  commands.securitygroup.command(ctx, name, add, remove, direction)

@main.command()
@click.option("--name", required=True, help="Ipset Friendly Name.")
@click.option("--add", multiple=True, help="Add IP range(s) to an ipset.")
@click.option("--remove", help="Remove IP ranges from an ipset by regular expression.")
@click.pass_context
def waf(ctx, name, add, remove):
  """Manages A Cloudfront Distribution's WAF IPSet
  """
  commands.waf.command(ctx, name, add, remove)

## main #########################################

if __name__ == "__main__":
  try:
    main(obj={})
  except Exception as e:
    traceback.print_exc()
    sys.exit(1)

  sys.exit(0)
