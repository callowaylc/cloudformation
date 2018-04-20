#!/usr/bin/env python3
import collections
import re
import sys

from lib.util import responds
from lib.logger import info, error, init_logger
from lib.aws import (
  sg,
  sg_remove_rules,
  sg_add_rules
)

def command(ctx, name, add, remove, direction):
  """Orchestrates AWS Security Group Profiles
  """
  trace = "commands#securitygroup#command"
  info("Enter", trace, {
    "ctx": ctx.obj,
    "name": name,
    "add": "add",
    "remove": remove,
    "direction": direction,
  })

  try:
    config = ctx.obj["profile"]["Config"]["Groups"][name]
  except Exception as e:
    error("Failed to determine config", trace, {
      "name": name,
      "error": e,
    })
    raise e

  info("Determined config", trace, { "name": name, "config": config, })

  if add:
    info("Operator chose to add ip ranges", trace, {
      "statements": add,
      "grep": "add-ip-ranges",
    })

    rules = [ ]
    for statement in add:
      info("Examining statement", trace, { "statement": statement, })

      try:
        tokens = __parse_tokens__(statement)
      except Exception as e:
        error("Failed to parse tokens", trace, {
          "statement": statement,
          "error": e,
        })
        raise e

      info("Parsed tokens", trace, { "statement": statement, "tokens": tokens, })
      rules.append(tokens)

    info("Determined all tokens", trace, {
      "statements": add,
      "rules": rules,
      "grep": "parsed-tokens-list",
    })

    # ensure that required data is present
    required = set([ "port", "protocol", "source" ])
    for tokens in rules:
      difference = required - set(tokens.keys())
      if difference:
        m = "Failed to supply required arguments"
        error(m, trace, { "required": list(difference), "tokens": tokens, })
        raise Exception(m)

    try:
      sg_add_rules(name, config["Vpc"], rules, direction, DRY=ctx.obj["dry"])
    except Exception as e:
      error("Failed to add rules", trace, {
        "name": name,
        "rules": rules,
        "error": error,
      })
      raise e


  elif remove:
    info("Operator chose to remove ip ranges", trace, {
      "statement": remove,
    })

    # values passed to remove may look like "port=.; protocol=tcp"
    # we need to parse these name/value pairs and evaluate regular expression
    # of each
    tokens = None
    try:
      tokens = __parse_tokens__(remove)
    except Exception as e:
      error("Failed to parse tokens", trace, {
        "statement": remove,
        "error": e,
      })
      raise e

    info("Determined tokens", trace, { "tokens": tokens, })

    # evaluate regular expressions for token values
    try:
      for k, v in tokens.items():
        tokens[k] = re.compile(v)
    except Exception as e:
      error("Failed to parse regular expression for token", trace, {
        "tokens": tokens,
        "error": e,
      })
      raise e

    info("Determined tokens after re compilation", trace, { "tokens": tokens, })

    try:
      removed = sg_remove_rules(name, config["Vpc"], tokens, direction, DRY=ctx.obj["dry"])
    except Exception as e:
      error("Failed to remove rules", trace, {
        "name": name,
        "expression": remove,
        "error": e,
      })
      raise e

    info("Removed security group rules", trace, { "removed": removed, })

  group = sg(name, config["Vpc"])
  info("Determined security group", trace, { "group": group, })

  # build response to be written viewed by operator
  response = [ ]
  key = "IpPermissions" if direction == "ingress" else \
        "IpPermissionsEgress"
  for rule in group[key]:
    info("Building response object for rule", trace, { "rule": rule, })

    grouping, ident = [ "IpRanges", "CidrIp" ] if len(rule["IpRanges"]) else \
                      [ "UserIdGroupPairs", "GroupId" ]
    source = [ r[ident] for r in rule[grouping] ]
    record = collections.OrderedDict([
      ( "type", direction ),
      ( "protocol", rule["IpProtocol"] ),
      ( "port", rule["FromPort"] if "FromPort" in rule else None ),
      ( "source", source ),
    ])
    response.append(record)
    info("Built response record", trace, { "record": record, })

  responds(response)
  info("Exit", trace)

def __parse_tokens__(string):
  """Parses key=value; pairs
  """
  trace = "commands#securitygroup#__parse_tokens__"
  info("Enter", trace, { "string": string, })

  matches = re.findall(r"(?P<key>.+?)\=(?P<value>.+?)(\;|$)", string)
  tokens = {
    group[0].strip(): group[1].strip()
    for group in matches
  }

  info("Exit", trace, { "returns": tokens })
  return tokens
