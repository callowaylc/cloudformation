#!/usr/bin/env python3
import sys
import os
import re
import boto3
from functools import lru_cache

from lib.logger import info, error

def sg_add_rules(name, vpc_id, rules, direction, Region="us-east-1", DRY=False):
  """Add rule to security group
  """
  trace = "aws#sg_add_rule"
  info("Enter", trace, {
    "name": name,
    "vpc_id": vpc_id,
    "rules": rules,
    "direction": direction,
    "Region": Region,
    "DRY": DRY,
  })

  client = boto3.client("ec2")
  removed = [ ]
  group = None

  try:
    group = sg(name, vpc_id, Region=Region)
  except Exception as e:
    error("Failed to get security group", trace, {
      "name": name,
      "vpc_id": vpc_id,
      "error": e,
    })
    raise e

  info("Determined group", trace, { "group": group, })

  # iterate through rules and build out ip permissions
  permissions = [ ]
  for tokens in rules:
    info("Examining tokens to build permission ruleset", trace, {
      "tokens": tokens,
    })
    p = {
      "FromPort": int(tokens["port"]),
      "ToPort": int(tokens["port"]),
      "IpProtocol": tokens["protocol"],
    }

    # check if cidr or source security group id
    if re.match(r"^sg", tokens["source"]):
      p["UserIdGroupPairs"] = [{
        "GroupId": tokens["source"],
        "Description": tokens["description"] if "description" in tokens.keys() else "",
      }]

    else:
      p["IpRanges"] = [{
        "CidrIp": tokens["source"],
        "Description": tokens["description"] if "description" in tokens.keys() else "",
      }]

    info("Determined permission ruleset", trace, {
      "permission": p,
      "grep": "permission-ruleset",
    })
    permissions.append(p)

  # finally, update security group
  handle = getattr(
    client, "authorize_security_group_%s" % direction
  )
  arguments = {
    "GroupId": group["GroupId"],
    "IpPermissions": permissions,
  }
  info("Adding security group permissions", trace, {
    "handle": handle,
    "type": direction,
    "handle_name": "authorize_security_group_%s" % direction,
    "arguments": arguments,
    "grep": "adding-security-group-permissions",
    "group": group,
  })

  if not DRY:
    try:
      response = handle(**arguments)
    except Exception as e:
      error("Failed to update security group", trace, {
        "arguments": arguments,
        "group": group,
        "error": e,
      })
      raise e

    info("Updated security group rules", trace, {
      "response": response,
      "group_id": group["GroupId"],
      "grep": "updated-security-group",
    })

  info("Exit", trace)

def sg_remove_rules(name, vpc_id, tokens, direction, Region="us-east-1", DRY=False):
  """Removes rules from security group
  """
  trace = "aws#sg_remove_rules"
  info("Enter", trace, {
    "name": name,
    "vpc_id": vpc_id,
    "tokens": tokens,
    "direction": direction,
    "Region": Region,
    "DRY": DRY,
  })

  client = boto3.client("ec2")
  removed = [ ]
  group = None

  try:
    group = sg(name, vpc_id, Region=Region)
  except Exception as e:
    error("Failed to get security group", trace, {
      "name": name,
      "vpc_id": vpc_id,
      "error": e,
    })
    raise e

  info("Determined group", trace, { "group": group, })

  key = "IpPermissions" if direction == "ingress" else \
        "IpPermissionsEgress"
  for rule in group[key]:
    info("Examining rule", trace, {
      "rule": rule,
      "grep": "examining-rule",
    })

    grouping, ident = [ "IpRanges", "CidrIp" ] if len(rule["IpRanges"]) else \
                      [ "UserIdGroupPairs", "GroupId" ]
    sources = [ r[ident] for r in rule[grouping] ]
    info("Determined rule sources", trace, { "sources": sources, })

    # now lets check our token against the rule
    if "port" in tokens and tokens["port"].match(str(rule["FromPort"])):
      info("Matched port", trace, {
        "rule": rule,
        "port": rule["FromPort"],
        "expression": tokens["port"],
      })
      removed.append(rule)

    elif "protocol" in tokens and tokens["protocol"].match(rule["IpProtocol"]):
      info("Matched protocol", trace, {
        "rule": rule,
        "protol": rule["IpProtocol"],
        "expression": tokens["protocol"],
      })
      removed.append(rule)

    elif "source" in tokens and list(filter(tokens["source"].match, sources)):
      info("Matched source", trace, {
        "rule": rule,
        "sources": sources,
        "expression": tokens["source"],
        "grep": "matched-sources",
      })

      original = rule["IpRanges"]
      rule["IpRanges"] = [
        r
        for r in rule["IpRanges"]
        if re.match(tokens["source"], r["CidrIp"])
      ]
      info("Removed range that matched source", trace, {
        "ranges": rule["IpRanges"],
        "original": original,
        "rule": rule,
        "grep": "removed-range-that-matched-source",
      })
      removed.append(rule)

    else:
      info("Keeping rule", trace, { "rule": rule, })

  # finally, lets update security group
  if removed:
    info("Found rules to remove", trace, {
      "remove": removed,
      "grep": "found-rules-to-remove",
    })

    handle = getattr(
      client, "revoke_security_group_%s" % direction
    )
    arguments = {
      "GroupId": group["GroupId"],
      "IpPermissions": removed,
    }
    info("Revoking security group permissions", trace, {
      "handle": handle,
      "handle_name": "revoke_security_group_%s" % direction,
      "arguments": arguments,
    })

    if not DRY:
      try:
        response = handle(**arguments)
      except Exception as e:
        error("Failed to update security group", trace, {
          "group": group,
          "error": error,
          "arguments": arguments,
        })
        raise e

      info("Updated security group rules", trace, {
        "group_id": group["GroupId"],
        "response": response,
      })
    else:
      info("Skipping group update because we are running dry", trace)

  info("Exit", trace, { "returns": removed })
  return removed

def sg(name, vpc_id, Region="us-east-1"):
  """Retrieves securitygroup by name and vpc id
  """
  trace = "aws#sg"
  info("Enter", trace, {
    "name": name,
    "vpc_id": vpc_id,
    "Region": Region
  })

  group = None
  response = None
  client = boto3.client("ec2")

  try:
    response = client.describe_security_groups(
      Filters=[
        {
          "Name": "vpc-id",
          "Values": [ vpc_id ],
        },
        {
          "Name": "group-name",
          "Values": [ name ],
        },
      ],
    )
  except Exception as e:
    error("Failed to list security groups", trace, {
      "vpc_id": vpc_id,
      "error": e,
    })
    raise e

  info("Determined groups", trace, { "groups": response, })

  try:
    group = response["SecurityGroups"][0]
  except Exception as e:
    error("Failed to determine matching group", trace, {
      "error": e,
      "groups": response["SecurityGroups"],
    })
    raise e

  info("Determined security group", trace, { "group": group })

  info("Exit", trace, { "returns": group })
  return group

def waf_ipset_add_ips(_id, ranges, DRY=False):
  """Add ip range(s) to a waf ipset
  """
  trace = "aws#waf_ipset_add_ips"
  info("Enter", trace, {
    "id": _id,
    "ranges": ranges,
    "DRY": DRY,
  })

  response = None
  client = boto3.client("waf")

  updates = [
    {
      "Action": "INSERT",
      "IPSetDescriptor": {
        "Type": "IPV6" if ":" in r else "IPV4",
        "Value": r
      },
    }
    for r in ranges
  ]
  info("Determined updates", trace, {
    "updates": updates,
    "id": _id,
  })

  if DRY:
    info("Skipping ipset update because we are running dry", trace)

  else:
    try:
      response = client.get_change_token()
      info("Determined change token", trace, { "token": response })

      response = client.update_ip_set(
        IPSetId=_id,
        ChangeToken=response["ChangeToken"],
        Updates=updates,
      )
    except Exception as e:
      error("Failed to update ipset", trace, {
        "updates": updates,
        "id": _id,
        "error": e,
      })
      raise e

  info("Added ip ranges to ipset", trace, {
    "ranges": ranges,
    "response": response,
  })
  info("Exit", trace)

def waf_ipset_remove_ips(_id, expression, DRY=False):
  """Check ipset for ips that match expression and remove them
  """
  trace = "aws#waf_ipset_remove_ips"
  info("Enter", trace, {
    "id": _id,
    "expression": expression,
    "DRY": DRY,
  })

  response = None
  client = boto3.client("waf")
  try:
    response = client.get_ip_set( IPSetId=_id )
  except Exception as e:
    error("Failed to determine ipset", trace, {
      "id": _id,
      "error": e,
    })
    raise e

  info("Determined ipset", trace, { "ipset": response })

  matches = [ ]
  for d in response["IPSet"]["IPSetDescriptors"]:
    if re.search(expression, d["Value"]):
      info("Found matching range", trace, { "ip": d["Value"] })
      matches.append(d["Value"])

  info("Found matching ranges", trace, { "matches": matches })

  if matches:
    # compose list of dicts that represents updates
    # http://boto3.readthedocs.io/en/latest/reference/services/waf.html#WAF.Client.update_ip_set
    updates = [
      {
        "Action": "DELETE",
        "IPSetDescriptor": {
          "Type": "IPV6" if ":" in r else "IPV4",
          "Value": r
        },
      }
      for r in matches
    ]
    info("Determined updates", trace, { "updates": updates, "id": _id, })

    if DRY:
      info("Skipping ipset update because we are running dry", trace)

    else:
      try:
        response = client.get_change_token()
        info("Determined change token", trace, { "token": response })

        response = client.update_ip_set(
          IPSetId=_id,
          ChangeToken=response["ChangeToken"],
          Updates=updates,
        )
      except Exception as e:
        error("Failed to update ipset", trace, {
          "updates": updates,
          "id": _id,
          "error": e,
        })
        raise e

  info("Exit", trace, { "returns": matches })
  return matches

def waf_ipset_ranges(_id):
  """Retrieves all ipsets' ranges associated to a ipset id
  """
  trace = "aws#waf_ipset_ranges"
  info("Enter", trace, { "id": _id})

  client = boto3.client("waf")
  ranges = [ ]
  response = None

  try:
    response = client.get_ip_set( IPSetId=_id )
  except Exception as e:
    error("Failed to determine ipset", trace, {
      "id": _id,
      "error": e,
    })
    raise e

  info("Determined ipset", trace, { "ipset": response })

  for descriptor in response["IPSet"]["IPSetDescriptors"]:
    info("Examining descriptor", trace, { "descriptor": descriptor })
    ranges.append(descriptor["Value"])

  info("Determnied ranges associated to ipset id", trace, {
    "id": _id,
    "ranges": ranges,
  })

  info("Exit", trace, { "returns": ranges })
  return ranges

@lru_cache(maxsize=None)
def waf_ipsets_ids(_id):
  """Retrieves all ipsets' ids associated to a waf web acl

  Retrieves all ipsets' ids associated to a waf web acl. To do so
  we must follow node relationships, from waf web-acl, to waf rule to
  ipsets
  """
  trace="aws#waf_ipsets_ids"
  info("Enter", trace, { "id": _id, })

  ids = None
  client = boto3.client("waf")
  response = None
  try:
    response = client.get_web_acl( WebACLId=_id )
  except Exception as e:
    error("Failed to retrieve waf web-acl", trace, {
      "id": _id,
      "error": error,
    })
    raise e

  info("Determined waf web-acl", trace, {
    "web_acl": response,
  })

  for rule in response["WebACL"]["Rules"]:
    info("Examining rule", trace, {
      "rule": rule,
      "id": rule["RuleId"],
    })

    try:
      response = client.get_rule( RuleId=rule["RuleId"] )
    except Exception as e:
      error("Failed to determine rule", trace, {
        "id": rule["RuleId"],
        "error": error,
      })
      raise e

    info("Determined rule object", trace, { "rule": response })

    # filter out ipset ids
    ids = [
      predicate["DataId"]
      for predicate in response["Rule"]["Predicates"]
      if predicate["Type"] == "IPMatch"
    ]

  info("Determnied ipset ids associated to web acl", trace, {
    "acl": _id,
    "ids": ids,
  })

  info("Exit", trace, { "returns": ids })
  return ids

def cloudfront_distribution(arn):
  """Retrieves cloudfront distribution by arn
  """
  trace = "aws#cloudfront_distribution"
  info("Enter", trace, { "arn": arn, })

  client = boto3.client("cloudfront")
  distribution = None
  try:
    distribution = client.get_distribution(
      Id=re.sub(r"^.+\/", "", arn)
    )
  except Exception as e:
    error("Failed to retrieve distribution", trace, {
      "error": e,
      "arn": arn,
    })
    raise e

  info("Exit", trace, { "returns": distribution })
  return distribution

def s3_push(bucket, path_local, path_remote):
  """Uploads artifact to AWS S3 and returns unsigned url
  """
  trace = "aws#s3_push"
  info("Enter", trace, {
    "bucket": bucket,
    "path_local": path_local,
    "path_remote": path_remote,
  })

  client = boto3.client('s3')
  client.upload_file(path_local, bucket, path_remote)

  returns = "https://s3.amazonaws.com/%s/%s" % ( bucket, path_remote )
  info("Exit", trace, { "returns": returns })
  return returns

def cloudformation_orchestrate(
  profile,
  Url=None,
  Content=None,
  DisableRollback=False,
  DisableBucket=False,
  Capabilities=False
):
  """Orchestrates the cloudformation template identified by url
  """
  trace = "aws#cloudformation_orchestrate"
  info("Enter", trace, {
    "profile": profile,
    "Url": Url,
    "Content": Content,
    "DisableRollback": DisableRollback,
    "DisableBucket": DisableBucket,
    "Capabilities": Capabilities,
  })
  client = boto3.client("cloudformation", region_name=profile["Region"])

  # determine if stack exists
  exists = True
  try:
    client.describe_stacks(StackName=profile["Stack"])
    info("Stack exists", trace, { "stack": profile["Stack"] })
  except:
    info("Stack does not exist", trace, { "stack": profile["Stack"] })
    exists = False

  inputs = profile["Inputs"] if "Inputs" in profile else { }
  parameters = __transform_stack_inputs__(inputs)
  info("Stack has the following parameters", trace, {
    "parameters": parameters,
  })

  # determine arguments to pass to create/update stack
  arguments = {
    "StackName": profile["Stack"],
    "Parameters": parameters,
  }
  if DisableBucket:
    arguments["TemplateBody"] = Content
  else:
    arguments["TemplateURL"] = Url

  if Capabilities:
    arguments["Capabilities"] = [ "CAPABILITY_NAMED_IAM" ]

  wait = None
  if exists:
    r = client.update_stack(**arguments)
    waiter = client.get_waiter("stack_update_complete")

  else:
    arguments["DisableRollback"] = DisableRollback
    r = client.create_stack(**arguments)
    waiter = client.get_waiter("stack_create_complete")

  error("Waiting for stack orchestrating to complete", trace, {
    "waiter": waiter,
  })
  waiter.wait(
    StackName=profile["Stack"],
  )

  info("Orchestrated stack", trace, {
    "result": r,
  })

def __transform_stack_inputs__(inputs):
  """Transforms key:value dictionary to form acceptable to
     boto3 cloudformation
  """
  return [
    { "ParameterKey": key, "ParameterValue": value }
    for key, value in inputs.items()
  ]