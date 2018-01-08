image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
#redis_nets='discogs-redis-site-queries discogs-metadata-stores discogs-redis-caches'

docker stop $container_name
docker rm $container_name

docker run \
    -di --restart=always \
    -p 70:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name
docker network connect discogs-redis-caches $container_name
#for net in $redis_nets ; do docker network connect $net $container_name ; done
