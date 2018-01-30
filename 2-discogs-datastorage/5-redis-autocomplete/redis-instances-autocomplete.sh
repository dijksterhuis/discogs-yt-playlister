#!/bin/bash

network='discogs-redis-autocomplete'
container_names='discogs-redis-autocomplete-artist discogs-redis-autocomplete-release discogs-redis-autocomplete-label'
port=7500
docker network create $network

for container_name in $container_names ; 
do \
    docker run \
        -d \
        --restart=always \
        -p $port:6379 \
        -v $container_name:/data \
        --name $container_name \
        --network $network \
        redis:alpine redis-server --appendonly yes ; \
    echo $container_name' started.' ;\
    port=$(($port+1)) ;\
done