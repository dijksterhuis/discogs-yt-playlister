#!/bin/bash

image='dijksterhuis/discogs-flask-redis-api:dev'
container_name='rest-redis-video-urls'
container_command='python redis_videos_api.py'
networks='redis-videos-masters rest-videos'
port='127.0.0.1:91:5000'

docker stop $container_name

docker run -di --rm \
    -p $port \
    -v logs:/logging \
    --name $container_name \
    $image /bin/ash

for network in networks; do docker network connect $network $container_name ; done

docker exec -it $container_name /bin/ash -c $container_command