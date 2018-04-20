#!/bin/bash
# Like "torify" but passes aws session, in the environment, to command
# AWS_PROFILE=test ./bin/awsify.sh echo \$AWS_SESSION_TOKEN
set -Eeuo pipefail

if [[ $# -eq 0 ]]; then
  echo "You must pass a command."
  exit 1
fi

AWS_PROFILE=${AWS_PROFILE:-""}
if [[ -z "$AWS_PROFILE" ]]; then
  echo "AWS_PROFILE must be defined."
  exit 2
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

AWS_ACCESS_KEY_ID=`echo $session | awk '{ print \$1 }'` \
AWS_SECRET_ACCESS_KEY=`echo $session | awk '{ print \$2 }'` \
AWS_SESSION_TOKEN=`echo $session | awk '{ print \$3 }'` \
  eval "$@"
