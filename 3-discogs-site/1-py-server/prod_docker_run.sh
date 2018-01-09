image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
webserve_net='discogs-webserve'

docker stop $container_name
docker rm $container_name

docker run \
    -di --restart=always \
    -p 70:80 -p 127.0.0.1:9191:9191 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name
docker network connect $webserve_net $container_name