#!/bin/bash

image='dijksterhuis/redis-database-inserts:0.1.0'
container_name='discogs-metadata-extract'
container_command='/home/redis-ETL.py --verbose'
networks='discogs-mongo discogs-redis-querying discogs-metadata-stores'

docker run -di \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image /bin/ash

for network in $networks; do docker network connect $network $container_name ; done

echo 'Container connected to networks: '$networks

docker exec -i $container_name /bin/ash -c $container_command

docker stop $container_name ; docker rm $container_name