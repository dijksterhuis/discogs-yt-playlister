#!/bin/bash

container_name='discogs-metadata-extract'
container_command='/home/insert_metadata_masters_v2_sets_only.py --verbose'

docker stop $container_name
docker rm $container_name

docker run -di --rm \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    dijksterhuis/redis-database-inserts:dev /bin/ash

docker network connect discogs-mongo-api $container_name
docker network connect redis-querying $container_name
docker network connect perm-metadata-stores $container_name

docker exec -it $container_name /bin/ash -c $container_command