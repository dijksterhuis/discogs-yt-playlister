#!/bin/bash

# variable declarations

tag='ids-from-names'
image='dijksterhuis/discogs-flask-redis-api:'$tag
container_names='discogs-get-relname-id discogs-get-artname-id' #discogs-get-lblname-id
numb_containers=$(echo $container_names | wc -w)
api_net='discogs-get-apis'
redis_net='discogs-redis-site-queries'

# container logic

function bring_up_container {
    docker stop $container_name ; docker rm $container_name ; \
    docker run -di --restart=always -v logs:/logging --name $container_name $image ; \
    echo $container_name' started.' ; \
    docker network connect $api_net $container_name ; \
    docker network connect $redis_net $container_name ; \
    echo $container_name' connected to networks '$api_net' & '$redis_net'.' ; \
    echo $container_name' UP.' ; \
}

# create networks if they don't already exist

docker network create $api_net
docker network create $redis_net

# script logic

if [ numb_containers > 1 ]; then \
    for container_name in $container_names ; \
        do bring_up_container ; \
    done ;\
else \
    container_name=$container_names
    bring_up_container ; \
fi