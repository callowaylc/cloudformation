#!/usr/bin/env python3
import collections
import re
import sys
import os

from lib.util import responds
from lib.logger import info, error, init_logger
from lib.util import resource_content, create_artifact, responds
from lib.aws import (
  s3_push,
  cloudformation_orchestrate,
  cloudfront_distribution,
)

def command(ctx, timeout, disable_rollback, disable_bucket, capabilities, sets):
  """Orchestrates AWS Cloudformation Profiles
  """
  trace = "commands#cloudformation#command"
  info("Enter", trace, {
   "ctx": ctx,
   "timeout": timeout,
   "disable_rollback": disable_rollback,
   "disable_bucket": disable_bucket,
   "capabilities": capabilities,
  })

  # evaluate sets
  profile = ctx.obj["profile"]
  expression = None
  try:
    for statement in sets:
      info("Evaluating statement.", trace, { "statement": statement, })

      root = Box(profile)
      content = 'root.%(statement)s' % {
        "root": root, "statement": statement,
      }
      info("Evaluating expression.", trace, {
        "root": root,
        "content": content,
      })

      exec(content)
      profile = root.to_dict()
      info("Merged evaluated expression onto profile.", trace, {
        "profile": root.to_dict(),
        "grep": "merged-expression",
      })
  except Exception as e:
    error("Failed to evaluate expression.", trace, {
      "expression": expression,
      "error": e,
    })
    raise e

  info("Evaluated sets against profile.", trace, {
    "profile": profile,
    "grep": "evaluated-sets",
  })

  # load template specified in profile
  content = None
  paths = os.environ.get("PATH_TEMPLATES", "./templates")
  if "Template" in profile:
    try:
      content = resource_content(profile["Template"], paths, profile)
    except Exception as e:
      error("Failed to load template", trace, {
        "template": profile["Template"],
        "paths": paths,
        "error": e,
      })
      raise e
  else:
    message = "Failed to define a 'Template' in profile"
    error(message, trace, { "profile": profile })
    raise Exception(message)

  info("Determined template content", trace, { "content": content, })

  # write interpolated template to build directory
  path = create_artifact(profile["Template"], content)
  info("Determined artifact path", trace, { "path": path, })

  uri = None
  if not disable_bucket:
    if "Stack" in profile:
      path_remote = "stack/%s/%s/%s" % (
        profile["Stack"],
        os.path.splitext(profile["Template"])[0],
        os.path.basename(path),
      )
      info("Pushing artifact to remote path", trace, {
        "path_remote": path_remote
      })
      try:
        uri = s3_push(os.environ["BUCKET"], path, path_remote)
      except Exception as e:
        error("Failed to push artifact to s3", trace, {
          "path_local": path,
          "path_remote": path_remote,
          "error": e
        })
        raise e
    else:
      message = "Failed to define a 'Stack' in profile"
      error(message, trace, { "profile": profile, })
      raise Exception(message)

    info("Pushed artifact to s3", trace, { "uri": uri, })


  # finally orchestrtate stack
  try:
    cloudformation_orchestrate(
      profile,
      Url=uri,
      Content=content,
      DisableRollback=disable_rollback,
      DisableBucket=disable_bucket,
      Capabilities=capabilities or (
        "Capabilities" in profile and profile["Capabilities"]
      )
    )
  except Exception as e:

    # check for stupid no update error which should be swallowed
    # https://github.com/hashicorp/terraform/issues/5653
    # https://www.reddit.com/r/aws/comments/5df50i/cloudformation_what_is_the_rationale_behind_not/
    if re.search(r"no updates are to be performed", str(e),re.IGNORECASE):
      error("Did not orchestrate stack because there are no changes", trace)

    else:
      error("Failed to orchestrate stack", trace, { "error": e, })
      raise e