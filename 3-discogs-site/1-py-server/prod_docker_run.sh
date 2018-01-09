image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving"
api_net='discogs-get-apis'

docker stop $container_name
docker rm $container_name

docker run \
    -it --restart=always \
    -p 75:80 -p 127.0.0.1:9191:9191 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name