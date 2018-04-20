# CHANGELOG cloudformation

## Version 5.0.5
**BUG FIX**: Add fallback to image `cloudformation/cloudformation` if image has not yet been tagged
**BUG FIX**: Fix pytest suites broken tests since version `5.0.0`

## Version 5.0.4
**BUG FIX**: Fix issue with multiple rules being incorrectly removed from security group

## Version 5.0.3
**BUG FIX**: Small update to `README.md`

## Version 5.0.2
**BUG FIX**: Fix make targets `bootstrap` and `orchestrate`

## Version 5.0.1
**BUG FIX**: Add dynamic lookup for aws registry to `./bin/cloudformation.sh`

## Version 5.0.0
**NEW FEATURE**: Add functionality for cloudformationi cli command `waf`
**NEW FEATURE**: Add functionality for cloudformationi cli command `securitygroup`
**ENHANCEMENT**: Update docker build workflow to allow for obfuscating cloudformation cli

## Version 4.0.2
**ENHANCEMENT**: Update readme to cover cloudformation cli.

## Version 4.0.1
**BUG FIX**: Remove security group template and profile, `templates/security-group-stack.yaml.j2` and `profiles/test.security-group-stack.yaml.j2`

## Version 4.0.0
**NEW FEATURE**: Add comprehensive cli, [cloudformation](./src/cloudformation.py), to manage securitygroups, waf and cloudformation
**ENHANCEMENT**: Refactor runner.py into `src/cloudformation.py`
**ENHANCEMENT**: Change name of profiles to $environment.$template
**ENHANCEMENT**: Refactor `Dockerfile` around `python:3.6.4-alpine3.7`
**ENHANCEMENT**: Small cleanup of `Makefile` around changes to cloudformation cli

## Version 3.2.1
**BUG FIX**: Set default value of environment variables TAG to nil

## Version 3.2.0
**ENHANCEMENT**: Add `PORT` environment variable to container environment.

## Version 3.1.0
**ENHANCEMENT**: Update `templates/ecs-task.yaml` to allow for passing environment variables via parameters
**ENHANCEMENT**: Add additional tests `test_environment_variables` and `test_artifact`
**ENHANCEMENT**: Update sanity check template to use environment variable `AWS_CLOUDFORMATION_BUCKET_DOMAIN`
**ENHANCEMENT**: Add `Dockerfile` arguments for cloudformation and lambda buckets and their respective domains

## Version 3.0.0
**ENHANCEMENT**: Add role "ecr" to bootstrap process defined in template `bootstrap.yaml.j2`
**ENHANCEMENT**: Add role "rds-monitoring" to bootstrap process defined in template `bootstrap.yaml.j2`

## Version 2.1.1
**BUG FIX**: Remove hardcoded `AWS_PROFILE=test` from `Makefile.functions`

## Version 2.1.0
**ENHANCEMENT**: Add test for profile interpolation `test_runner.py#test_load_profile_with_env`

## Version 2.0.0
**NEW FEATURE**: Add interpolation of data profiles through jinja2 template engine

## Version 1.3.0
**ENHANCEMENT**: Add Scheduler To Generic Template `templates/ecs-task.yaml`

## Version 1.2.0
**NEW FEATURE**: Add [waiter](http://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html#waiters) to stack orchestration to `runner.py#orchestrate`
**ENHANCEMENT** Add DeletionPolicy of delete to generic templates `user.yaml`, `role.yaml`, `group.yaml` and `policy.yaml`

## Version 1.1.0
**ENHANCEMENT**: Added generic cloudformation for policy in `templates/policy.yaml`
**ENHANCEMENT**: Added generic cloudformation for user in `templates/user.yaml`
**ENHANCEMENT**: Added generic cloudformation for role in `templates/role.yaml`
**ENHANCEMENT**: Added generic cloudformation for group in `templates/group.yaml`

## Version 1.0.0
**NEW FEATURE**: Initial Release
