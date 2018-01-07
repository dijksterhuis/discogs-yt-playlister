#!/bin/bash

docker network create discogs-get-apis

image='dijksterhuis/discogs-flask-redis-api:dev'
port_number=10000
container_names='discogs-get-videos discogs-get-relname-id discogs-get-artname-id discogs-get-metadata-id discogs-get-metadata-unique'
container_command='python /home/redis_api_ids_from_names.py'

for container_name in $container_names ; \
    do \
        port='127.0.0.1:'$port_number':5000' ; \
        docker rm -f $container_name ; \
        docker run -di --restart=always -p $port -v logs:/logging --name $container_name $image /bin/ash ; \
        echo $container_name' started.' ; \
        docker network connect discogs-get-apis $container_name ; \
        if [ $container_name = 'discogs-get-metadata-id' ] || [ $container_name = 'discogs-get-metadata-unique' ] ; \
            then \
                docker network connect discogs-metadata-stores $container_name ; \
                echo $container_name' connected to network discogs-metadata-stores.' ; \
            else \
                docker network connect discogs-redis-site-queries $container_name ; \
                echo $container_name' connected to network discogs-redis-site-queries.' ; \
        fi ; \
        docker exec -d $container_name /bin/ash -c $container_command ; \
        echo $container_name' running.' ; \
        $port_number=$(($port_number+1)) ; \
    done