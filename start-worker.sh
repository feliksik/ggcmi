#!/bin/bash

. config.sh

if [ "$GGCMI_MYSQL_HOST"="$TEST_MYSQL_CONTAINER_NAME" ]; then
  echo 'Using Docker test container for mysql, because $GGCMI_MYSQL_HOST==$TEST_MYSQL_CONTAINER_NAME '
  ./start-mysql.sh || exit 1
  export LINK_TO_MYSQL_CONTAINER="--link $TEST_MYSQL_CONTAINER_NAME:$TEST_MYSQL_CONTAINER_NAME"
fi

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
