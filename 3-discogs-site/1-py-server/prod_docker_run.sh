image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
networks='discogs-get-apis'
numb_nets=$(echo $container_names | wc -w)

docker run \
    -di --restart=always \
    -p 127.0.0.1:80:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

if [ numb_nets > 1 ]; then \
    for net in $networks ; do docker network connect $net $container_name ; done ; \
else \
    docker network connect $networks $container_name ; \
fi

