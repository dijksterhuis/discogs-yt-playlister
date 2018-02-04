#!/bin/bash

image='dijksterhuis/redis-database-inserts:modularised-0.1'
container_name='redis-loads-labels-ids'
container_command='./redis-load-set-adder.py'
# run_type, primary_key, mongo instance, redis instance, key, value
# ---! N.B. IF MONGO RELEASES DATA HASN'T BEEN RELOADED, master_id NEEDS TO BE SWAPPED WITH #text
container_args='simple key releases redis-labels-ids label_name master_id'
networks='discogs-redis-site-queries discogs-mongo'

docker run -di \
    -w /home \
    -v metadata-extraction-logs:/logging \
    --name $container_name \
    $image

for network in $networks; do docker network connect $network $container_name ; echo "connected to "$network ; done

docker exec -i $container_name $container_command $container_args

docker stop $container_name ; docker rm $container_name