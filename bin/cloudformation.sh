#!/bin/bash
# Description: A shell wrapper for executing cloudformation cli; requires an IAM user to
# to assume role with appropriate permissions.
# Usage: cloudformation.sh --help
set -Eeuo pipefail

arguments=$@
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

AWS_PROFILE=${AWS_PROFILE:-""}
if [[ -z "$AWS_PROFILE" ]]; then
  echo "AWS_PROFILE must be defined."
  exit 1
fi

# get image
image=$(
  aws ecr get-login --no-include-email --region $AWS_DEFAULT_REGION \
    | awk -F'/' '{ print $NF }'
)
image=$image/cloudformation/cloudformation

# check if image is defined
if ! docker images | grep -i $image >/dev/null 2>&1; then
  image=cloudformation/cloudformation
fi

# from our identity, we can get account-id, role and a session-name
identity=$(
  aws sts get-caller-identity --output text --query '[Account,UserId,Arn]'
)
account=`echo $identity | awk '{ print $1 }'`
role=`echo $identity | awk -F'/' '{ print $(NF-1) }'`
name=`echo $identity | awk -F'/' '{ print $NF }'`

# from account-id, role and session-name, we can grab temporary credentials
# namely an access key, secret and session token
session=$(
  aws sts assume-role \
    --role-arn=arn:aws:iam::$account:role/$role \
    --role-session-name=$name \
    --output text \
    --query "Credentials.{AKI:AccessKeyId, SAK:SecretAccessKey, ST:SessionToken}"
)

# remove all extra spaces after ; characters
arguments=`echo $arguments | sed 's/; */;/g'`

# we now pass our temporary credentials to the container and execute
# the cloudformation cli with whatever arguments have been passed
docker run \
  --rm \
  -it \
  --volume `pwd`/profiles:/opt/bin/profiles \
  --volume `pwd`/templates:/opt/bin/templates \
  --env AWS_ACCESS_KEY_ID=`echo $session | awk '{ print \$1 }'` \
  --env AWS_SECRET_ACCESS_KEY=`echo $session | awk '{ print \$2 }'` \
  --env AWS_SESSION_TOKEN=`echo $session | awk '{ print \$3 }'` \
  --env AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    $image $arguments
