#!/bin/bash

network='discogs-redis-caches'
container_names='discogs-session-query-cache discogs-user-session-cache' 
port=7200
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
        redis:alpine redis-server ; \
    echo $container_name' started.' ;\
    $port=$(($port+1)) ;\
done

##### NOTES:
# ------------------------------------------------------------------
###### discogs-session-query-cache
# ----------------------------------------------------------------
# store the session results that a user has confirmed for query
# store video ids as sets per user session (delete key once sent to youtube)
# ----------------------------------------------------------------
###### redis-discogs-sessions
# ----------------------------------------------------------------
# store information about the user session

