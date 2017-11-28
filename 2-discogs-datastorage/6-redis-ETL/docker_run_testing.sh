#!/bin/bash

image='dijksterhuis/redis-database-inserts:dev'
container_name='discogs-metadata-extract'
container_command='/home/insert_metadata_masters_v2_sets_only.py --verbose'
networks='discogs-mongo-api redis-querying perm-metadata-stores'

docker run -di --rm \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image /bin/ash

for network in networks; do docker network connect $network $container_name ; done

docker exec -it $container_name /bin/ash -c $container_command

docker stop $container_name