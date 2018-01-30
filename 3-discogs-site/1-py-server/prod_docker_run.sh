image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
external_net='discogs-external-apis'

docker stop $container_name
docker rm $container_name

docker run \
    -di --restart=always \
    -p 80:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name
docker network connect --ip=172.25.0.2 $external_net $container_name