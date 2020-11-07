#!/usr/bin/env bash
set -e

echo Running with arguments $*

artifactszip=${1:-cdkartifacts.zip}
echo artifactszip is $artifactszip

# Set up virtual env
VIRTUAL_ENV=cdk_testvenv
virtualenv -p python3 $VIRTUAL_ENV
. $VIRTUAL_ENV/bin/activate

#Install requirements
pip install -r infra/src/requirements.txt

##Run tests
export PYTHONPATH=./infra

cdk --app  "python ./infra/src/app.py" synth --no-staging

#Zip artifacts
echo running zip $artifactszip -r cdk.out
zip $artifactszip -r cdk.out

# Deactivate virtual envs
deactivate
