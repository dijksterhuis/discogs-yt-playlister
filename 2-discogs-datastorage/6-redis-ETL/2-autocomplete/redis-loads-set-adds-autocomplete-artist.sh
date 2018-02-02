#!/bin/bash

image='dijksterhuis/redis-database-inserts:modularised-0.1'
container_name='redis-loads-autocomplete-artist'
container_command='./redis-load-set-adder.py'
# run_type, primary_key, mongo instance, redis instance, key, value
container_args='autocomplete value masters discogs-redis-autocomplete-artist masters_id artist_name'
networks='discogs-redis-autocomplete discogs-mongo'

docker run -di \
    -w /home \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image

for network in $networks; do docker network connect $network $container_name ; echo "connected to "$network ; done

docker exec -i $container_name $container_command $container_args

docker stop $container_name ; docker rm $container_name