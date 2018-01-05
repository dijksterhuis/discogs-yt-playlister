pth="/home/dijksterhuis/Documents/discogs-yt-playlister/3-discogs-site/1-py-server/flask-site"

image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
networks='discogs-metadata-stores discogs-redis-site-queries discogs-redis-caches'

docker run \
    -di --restart=always \
    -p 70:5000 \
    -v $pth:/home/site \
    -w /home \
    --name $container_name \
    $image_name":"$image_tag

for net in $networks ; do docker network connect $net $container_name ; done

docker exec -it $container_name /bin/ash -c "python /home/site/main.py"
docker stop $container_name; docker rm $container_name