#!/usr/bin/env python3
import os
import yaml
import time
import json
from jinja2 import Template
from datetime import datetime
from pprint import PrettyPrinter

from lib.logger import info, error

def responds(blob):
  """Responsible for writing to operator's device (most likely stdout)
  """
  print(json.dumps( blob, indent=4 ))

def create_artifact(file, content):
  """Writes content to build directory and returns path of artifact.
  """
  trace = "util#create_artifact"
  info("Enter", trace, {
    "content": content,
    "file": file,
  })

  # write interpolated content to build file
  ts = datetime.now().strftime("%Y%m%d%H%M%S")
  path = "./build/%s.%s" % (ts, file)
  with open(path, "w") as f:
    f.write(content)

  info("Exit", trace, { "returns": path, })
  return path


def resource_content(file, paths, context={ }):
  """Loads "resource" content from file and interpolates with context
  """
  trace = "util#resource_content"
  info("Enter", trace, {
    "file": file,
    "paths": paths,
    "context": context,
  })

  path = resource_path(file, paths)
  if not path:
    message = "Failed to find resource"
    error(message, trace, { "file": file, "paths": path, })
    raise Exception(message)

  info("Found resource file", trace, { "path": path })

  interpolated = None
  os.environ["TIMESTAMP"] = str(int(time.time()))
  context = { **{ "ENV": os.environ }, **context }
  info("Context to used for interpolation", trace, { "context": context, })

  with open(path, "r") as f:
    interpolated = Template(f.read()).render(context)

  info("Interpolated resource", trace, { "content": interpolated, })
  info("Exit", trace, { "returns": interpolated })
  return interpolated

def resource_path(file, paths):
  """Searches for file along colon delimited paths
  """
  trace = "util#resource_path"
  info("Enter", trace, { "file": file, "paths": paths, })

  path = None
  for path in paths.split(":"):
    fullpath = "%s/%s" % (path, file)
    info("Checking path", trace, { "path": path, "fullpath": fullpath, })
    if os.path.isfile(fullpath):
      path = fullpath
      break

  info("Exit", trace, { "returns": path, })
  return path
