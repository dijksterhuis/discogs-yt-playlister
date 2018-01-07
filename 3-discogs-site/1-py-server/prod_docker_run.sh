image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
redis_net='discogs-redis-site-queries'
numb_nets=$(echo $container_names | wc -w)

docker run \
    -di --restart=always \
    -p 70:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name
docker network connect $redis_net $container_name