#################################################
#
# settings of the mysql container, if you want to run it locally
#
export TEST_MYSQL_ADDR=localhost
export TEST_MYSQL_PORT=3306
export TEST_MYSQL_ROOT_PASSWORD=s3cr3t
export TEST_MYSQL_CONTAINER_NAME=ggcmi-mysql

# testdata for the docker-based MySQL server
export TEST_MYSQL_DATA=../data/Dump20141114.sql


#################################################
#
# settings of the worker container
#
export DB_USER=root
export DB_PASS=$TEST_MYSQL_ROOT_PASSWORD
# DB_HOST can include port
# use $TEST_MYSQL_CONTAINER_NAME to activate the local test mysql server in docker container
#export DB_HOST="alterra-ei-ggcmi.cihy1ytynivm.us-west-2.rds.amazonaws.com"
export DB_HOST=$TEST_MYSQL_CONTAINER_NAME
export DB_DATABASE=ggcmi

# limit nr of CPUs
# None: use all
# >0: use given number
# <0: keep given number idle
export NR_OF_CPUS=None

# host directories where worker containers reads/writes data
# use readlink to convert to absolute path, required for docker volume mounting
export GGCMI_INPUT_DATA_HOST=../data
export GGCMI_OUTPUT_DATA_HOST=../output

