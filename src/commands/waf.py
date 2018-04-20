#!/usr/bin/env python3
import collections
import re
import sys

from lib.util import responds
from lib.logger import info, error, init_logger
from lib.aws import (
  waf_ipset_ranges,
  waf_ipset_remove_ips,
  waf_ipset_add_ips,
)

def command(ctx, name, add, remove):
  """Manages A Cloudfront Distribution's WAF IPSet
  """
  trace = "commands#waf#command"
  info("Enter", trace, {
    "ctx": ctx.obj,
    "name": name,
    "add": add,
    "remove": remove,
  })

  # get distribution id
  profile = ctx.obj["profile"]
  config = None
  try:
    config = profile["Config"]["Groups"][name]
  except Exception as e:
    error("Failed to determine config", trace, {
      "name": name,
      "error": e,
    })
    raise e

  if add:
    info("Operator chose to add an ip range", trace, {
      "range": add,
    })

    info("Determined ipset id that range will be added to", trace, {
      "id": config["Id"],
      "range": add,
    })
    waf_ipset_add_ips(config["Id"], add, DRY=ctx.obj["dry"])

  elif remove:
    info("Operator chose to remove ip ranges", trace, {
      "expression": remove,
    })

    try:
      expression = re.compile(remove)
    except Exception as e:
      error("Failed compile remove pattern", trace, {
        "remove": remove,
        "error": e,
      })
      raise e

    info("Checking ipset for ips that match pattern", trace, { "id": config["Id"] })

    removed = waf_ipset_remove_ips(
      config["Id"], expression, DRY=ctx.obj["dry"]
    )
    if removed:
      info("Removed ip ranges from ipset", trace, {
        "id": config["Id"],
        "removed": removed,
        "grep": "removed-ip-ranges-from-ipset",
      })
    else:
      info("Did not remove any ip ranges because none were matched", trace, {
        "id": config["Id"],
      })

  ranges = waf_ipset_ranges(config["Id"])
  info("Determiend ranges", trace, {
    "ranges": ranges,
    "id": config["Id"],
  })
  responds(ranges)

  info("Exit", trace)
