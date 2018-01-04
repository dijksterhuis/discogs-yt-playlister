#!/bin/bash

image='dijksterhuis/redis-database-inserts:modularised-0.1'
container_name='discogs-testing'
container_command='masters redis-masters-ids release_title masters_id'
docker_network='discogs-redis-site-queries'
docker run -di \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    --network $docker_network
    $image container_command