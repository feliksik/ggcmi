PCSE
====

Repository for the Python Crop Simulation Environment

# Dependencies #

If you `git clone https://github.com/feliksik/ggcmi` in ~/basedir/, the directory ~/basedir/ggcmi is created. 
The Docker build file assumes that the following extra files/dirs exist (currently you have to put them there manually). 
* basedir/ggcmi/deps/
* basedir/ggcmi/deps/futil.so
* basedir/ggcmi/deps/netcdf-4.3.2.zip
* basedir/ggcmi/deps/netcdf4-python-master.zip
* basedir/data/
* basedir/data/Dump20141114.sql
* basedir/data/OtherInputs/...
* basedir/data/AgMERRA/...
* basedir/data/geodata/...
* basedir/output/

# Building #

You can run this repository in a docker container as follows: 

* install docker; on ubuntu you can do 
  * `curl -sSL https://get.docker.com/ubuntu/ | sudo sh`
* build the docker image
  * `docker build -t ggcmi .`
  * this will make it visible in the listing of `docker images`

# RUNNING #
* edit `config.sh` to your liking, and run: 
  * `./start-worker.sh`
  * it will run a worker with the configuration of `config.sh`
  * if your `config.sh` specifies ggcmi-mysql as the DB_HOST, this means you wish to run a local Docker-based mysql database. It will be started, if it does not already exist. 

Congratulations, you are now running the Global Gridded Crop Model Intercomparison (GGCMI) in a test environment! 

If you want to run with multiple worker nodes, you go as follows: 
* set up a MySQL database with the worker data on a central server
* on every worker node: 
  * install: 
    * the docker image
    * the required data directory
    * the `config.sh` configured to use the remote MySQL host (it is identical on each worker node)
  * `./start-worker.sh`
  * relax, and see results coming in



