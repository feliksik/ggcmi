FROM ubuntu:14.04
MAINTAINER Eric Feliksik


# Environment variables to set on docker run: 
# - DB_USER : database username
# - DB_PASS : database password
# - DB_HOST : hostname/ip address of db (may include port)
# - DB_DATABASE : name of database to use
# - DATA_INPUT_DIR : path of input-data dir; defaults to /opt/ggcmi-input 
# - DATA_OUTPUT_DIR : path of output data dir; defaults to /opt/ggcmi-output 
# - NR_OF_CPUS: the number of cpu cores to use (unset means use all cpus ; -n means leave n cores unused)


ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update
RUN apt-get -y install python-sqlalchemy python-numpy python-tables libhdf5-dev build-essential unzip curl libcurl3-gnutls libcurl3-gnutls-dev python-dev python-mysqldb ipython psmisc screen

# add repo
# install git repo for software
ADD pcse /opt/ggcmi/pcse
ADD src /opt/ggcmi/src


# add dependencies
ADD deps/netcdf-4.3.2.zip /tmp/netcdf-4.3.2.zip
WORKDIR /tmp/
RUN unzip netcdf-4.3.2.zip
WORKDIR /tmp/netcdf-4.3.2
RUN ./configure && make && make install 

ADD deps/netcdf4-python-master.zip /tmp/netcdf4-python-master.zip
WORKDIR /tmp/
RUN unzip netcdf4-python-master.zip
WORKDIR /tmp/netcdf4-python-master
RUN python setup.py install

ADD deps/futil.so /opt/ggcmi/pcse/pcse/futil.so


RUN mkdir /opt/ggcmi-data
RUN mkdir /opt/ggcmi-output




RUN rm -rf /tmp/netcdf*


WORKDIR /opt/ggcmi/src
#ENTRYPOINT ["/bin/bash ./start_ggcmi_batch.sh"]
ENTRYPOINT ["/bin/bash", "./start_ggcmi_batch.sh"]


