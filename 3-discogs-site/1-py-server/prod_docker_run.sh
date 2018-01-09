image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving"
api_net='discogs-get-apis'
<<<<<<< HEAD
=======
#redis_nets='discogs-redis-site-queries discogs-metadata-stores discogs-redis-caches'
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up

docker stop $container_name
docker rm $container_name

docker run \
    -di --restart=always \
<<<<<<< HEAD
    -p 70:80 -p 443:443 \
=======
    -p 70:80 \
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up
    -w /home \
    --name $container_name \
    $image_name":"$image_tag /bin/ash -c "python /app/main.py"

<<<<<<< HEAD
docker network connect --ip=172.23.0.2 $api_net $container_name
=======
docker network connect --ip=172.23.0.2 $api_net $container_name
docker network connect discogs-redis-caches $container_name
#for net in $redis_nets ; do docker network connect $net $container_name ; done
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up
