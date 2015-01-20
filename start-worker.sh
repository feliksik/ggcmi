#!/bin/bash
#
# This script helps you run the GGCMI docker container easily.
# It externalizes the configuration in config.sh , and does
# some basic sanity checking for the availability of external files. 
#
. config.sh

function die {
  echo "Error: $1" >/dev/stderr
  exit 1
}

# file should exist
[ -d "$GGCMI_INPUT_DATA_HOST" ] || die "Not a directory: $GGCMI_INPUT_DATA_HOST"
[ -d "$GGCMI_OUTPUT_DATA_HOST" ] || die "Not a directory: $GGCMI_OUTPUT_DATA_HOST"

if [ "$GGCMI_MYSQL_HOST"="$TEST_MYSQL_CONTAINER_NAME" ]; then
  echo 'Using Docker test container for mysql, because $GGCMI_MYSQL_HOST==$TEST_MYSQL_CONTAINER_NAME '
  ./start-mysql.sh || exit 1
  export LINK_TO_MYSQL_CONTAINER="--link $TEST_MYSQL_CONTAINER_NAME:$TEST_MYSQL_CONTAINER_NAME"
fi

# convert relative path to absolute, as docker requires
GGCMI_INPUT_DATA_HOST=$(readlink -e $GGCMI_INPUT_DATA_HOST)
GGCMI_OUTPUT_DATA_HOST=$(readlink -e $GGCMI_OUTPUT_DATA_HOST)

# start worker
echo 'start ggcmi worker container'
docker run -dti $LINK_TO_MYSQL_CONTAINER \
  -v $GGCMI_INPUT_DATA_HOST:/opt/ggcmi-input \
  -v $GGCMI_OUTPUT_DATA_HOST:/opt/ggcmi-output \
  -e DB_USER=$DB_USER \
  -e DB_PASS=$DB_PASS \
  -e DB_HOST=$DB_HOST \
  -e DB_DATABASE=$DB_DATABASE \
  -e NR_OF_CPUS=$NR_OF_CPUS \
  --name ggcmi \
  ggcmi
