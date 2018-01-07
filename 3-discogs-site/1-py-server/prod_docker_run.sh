image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
api_net='discogs-get-apis'
networks='discogs-redis-site-queries discogs-metadata-stores'
numb_nets=$(echo $container_names | wc -w)

docker run \
    -di --restart=always \
    -p 70:80 \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

docker network connect --ip=172.23.0.2 $api_net $container_name

if [ numb_nets > 1 ]; then \
    for net in $networks ; do docker network connect $net $container_name ; done ; \
else \
    docker network connect $networks $container_name ; \
fi

