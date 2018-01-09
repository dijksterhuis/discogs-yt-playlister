image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving"
api_net='discogs-get-apis'

docker stop $container_name
docker rm $container_name

docker run \
    -di --restart=always \
    -p 70:80 -p 443:443 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name