#!/bin/bash

image='dijksterhuis/redis-database-inserts:modularised-0.1'
container_name='redis-loads-autocomplete-label'
container_command='./redis-load-set-adder.py'
container_args='autocomplete releases discogs-redis-autocomplete-label masters_id label_name'
networks='discogs-redis-autocomplete discogs-mongo'

docker run -di \
    -w /home \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image

for network in $networks; do docker network connect $network $container_name ; echo "connected to "$network ; done

docker exec -i $container_name $container_command $container_args

docker stop $container_name ; docker rm $container_name