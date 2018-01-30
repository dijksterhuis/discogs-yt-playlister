#!/bin/bash
image='dijksterhuis/discogs-flask-redis-api:autocomplete'
container_name='discogs-get-autocomplete'
api_network='discogs-get-apis'
redis_network='discogs-redis-autocomplete'
ip_suffix=10
ip_prefix='172.23.0.'

docker stop $container_name ; docker rm $container_name

docker run -di --restart=always -v logs:/logging --name $container_name --network $redis_network $image

docker network connect --ip=$ip_prefix$ip_suffix $api_network $container_name

echo $container_name' UP.'
