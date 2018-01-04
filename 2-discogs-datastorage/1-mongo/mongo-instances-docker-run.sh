#!/bin/bash

### mongo-instances-docker-run.sh
# Sets up a network for all the databses, create individual docker volumes for each instance and start the instances
# To use:
# 1. Pass the following as arguments set up mongodb instances for all files:
# ./test.sh labels releases masters artists
# 2. Or pass one/two of the above to start a single instance:
# ./test.sh labels
# ./test.sh labels releases

# create a discgos-mongo network (if it already exists docker won't create it again)
docker network create discogs-mongo
# use each argument provided to .sh script as a name for instances
for instance_name in $@ ; \
do \
    \ # set up tmp variables for each instance
    conf_vol="discogs-"$instance_name"-mongo-conf" ;\
    data_vol="discogs-"$instance_name"-mongo-data" ;\
    inst_name="mongo-discogs-"$instance_name ; \
    \ # start up the DBs using tmp variables
    docker run \
        -dt \
        --restart=always \
        -v $conf_vol:/home \
        -v $data_vol:/data/db \
        --network discogs-mongo \
        --name $inst_name \
        mongo ; \
done