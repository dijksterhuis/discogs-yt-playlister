#!/bin/bash

image='dijksterhuis/redis-database-inserts:modularised-0.1'
container_name='discogs-testing'
container_command='./redis-load-set-adder.py masters redis-masters-ids release_title masters_id'
networks='discogs-redis-site-queries discogs-mongo'

docker run -di \
    -w /home \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image

for network in $networks; do docker network connect $network $container_name ; echo "connected to "$network ; done

docker exec -i $container_name /bin/ash -c $container_command

docker stop $container_name ; docker rm $container_name