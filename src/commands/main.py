#!/usr/bin/env python3
import os
import yaml

from lib.logger import info, error, init_logger
from lib.util import resource_content

def command(ctx, loglevel, profile, dry):
  init_logger(loglevel)
  trace = "commands#main#command"
  info("Enter", trace, {
    "ctx": ctx.obj,
    "loglevel": loglevel,
    "profile": profile,
    "dry": dry,
  })

  # load profile
  content = None
  paths = os.environ.get("PATH_PROFILES", "./profiles")
  try:
    content = resource_content(profile, paths)
  except Exception as e:
    error("Failed to load profile content", trace, { "error": e })
    raise e

  profile = None
  try:
    profile = yaml.load(content) or { }
  except Exception as e:
    error("Failed to load profile as yaml", trace, { "error": e })
    raise e

  info("Loaded profile", trace, { "profile": profile, "grep": "loaded-profile" })

  # place values into context
  ctx.obj["profile"] = profile
  ctx.obj["dry"] = dry
  info("Exit", trace)
