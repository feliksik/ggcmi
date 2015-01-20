#!/bin/bash

. config.sh

function die {
  echo "Error: $1" >/dev/stderr
  exit 1
}

# start database, if not running already
if ! docker ps | grep -q $TEST_MYSQL_CONTAINER_NAME; then

  if [ ! -e "$TEST_MYSQL_DATA" ]; then
    die "environment variable TEST_MYSQL_DATA is not a file: $TEST_MYSQL_DATA"
  fi
  export TEST_MYSQL_DATA_HOSTDIR=$(dirname $(readlink -e $TEST_MYSQL_DATA))
  export TEST_MYSQL_DATA_FILENAME=$(basename $(readlink -e $TEST_MYSQL_DATA))

  echo "start $TEST_MYSQL_CONTAINER_NAME server in container..."
  docker run --privileged=false --name $TEST_MYSQL_CONTAINER_NAME \
    -e MYSQL_ROOT_PASSWORD=$TEST_MYSQL_ROOT_PASSWORD \
    -e MYSQL_USER=$MYSQL_USER \
    -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
    -e MYSQL_DATABASE=$MYSQL_DATABASE \
    -d \
    mysql || die 'Cannot start container $TEST_MYSQL_CONTAINER_NAME'

  # wait until the container is started polling would be nicer)
  sleep 10

  echo "fill db with testdata..."
  docker run -it --link $TEST_MYSQL_CONTAINER_NAME:mysql \
    -v $TEST_MYSQL_DATA_HOSTDIR:/tmp/sql-data/ \
    --rm mysql sh -c \
    "exec mysql -h\"mysql\" \
    -P\"$TEST_MYSQL_PORT\" \
    -uroot \
    -p\"$TEST_MYSQL_ROOT_PASSWORD\" </tmp/sql-data/$TEST_MYSQL_DATA_FILENAME " || die 'Cannot load testdata into container'

  # must still update tasklist set status='Pending' limit 10;
  echo "activate tasks (set Pending)..."
docker run -it --link $TEST_MYSQL_CONTAINER_NAME:mysql \
    -v $TEST_MYSQL_DATA_HOSTDIR:/tmp \
    --rm mysql sh -c \
    "exec mysql -h\"mysql\" \
    -P\"$TEST_MYSQL_PORT\" \
    -uroot \
    -p\"$TEST_MYSQL_ROOT_PASSWORD\" \
    ggcmi -e \"update tasklist set status='Pending' limit 500\" " \
       || die 'Cannot set tasks to Pending'

else
    echo "Database already running, so not starting MySQL container "
fi

