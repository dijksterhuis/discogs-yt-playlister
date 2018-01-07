#!/bin/bash

network='discogs-metadata-stores'
container_names='redis-metadata-unique-genre redis-metadata-unique-style redis-metadata-unique-year redis-metadata-unique-reldate' 
port=7100
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
    echo $container_name' started.'
    $port=$(($port+1)) ;\
done

##### NOTES:
# ------------------------------------------------------------------
###### redis-metadata-unique-genre
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-style
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-year
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-reldata (month???)
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
