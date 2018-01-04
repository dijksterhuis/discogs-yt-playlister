#!/bin/bash

for tag in genre style year; \
do \
echo 'Running for tag '$tag ; \
image='dijksterhuis/redis-database-inserts:modularised-0.1' ;\
container_name='redis-loads-unique-'$tag ;\
container_command='./redis-load-set-adder.py ; exit' ;\
container_args='simple_set masters redis-metadata-unique-'$tag' '$tag' masters_id' ;\
networks='discogs-metadata-stores discogs-mongo' ;\
echo $container_name ; echo $image ;\
        docker run -di \
            -w /home \
            -v metadata-extraction-logs:/logging \
            --name $container_name \
            $image ; \
         for network in $networks; do docker network connect $network $container_name ; echo "connected to "$network ; done ; \
        docker exec -di $container_name $container_command $container_args ; \
; done

        #docker stop $container_name ; docker rm $container_name \