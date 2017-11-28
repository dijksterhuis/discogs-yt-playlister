#!/bin/bash

image='dijksterhuis/redis-database-inserts:dev2'
container_name='discogs-metadata-extract'
container_command='/home/redis-ETL.py --verbose'
networks='discogs-mongo discogs-redis-querying discogs-metadata-stores'

docker run -it --rm \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image /bin/ash

for network in $networks; do docker network connect $network $container_name ; done

docker exec -it $container_name /bin/ash -c $container_command

docker stop $container_name