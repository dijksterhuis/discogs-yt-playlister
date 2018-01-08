image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
numb_nets=$(echo $container_names | wc -w)
redis_nets='discogs-redis-site-queries discogs-metadata-stores'

docker stop $container_name
docker rm $container_name

docker run \
    -it --restart=always \
    -p 70:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

#docker network connect --ip=172.23.0.2 $api_net $container_name
#for net in $redis_nets ; do docker network connect $net $container_name ; done
