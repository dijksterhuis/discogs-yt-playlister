pth="/home/dijksterhuis/Documents/discogs-yt-playlister/3-discogs-site/1-py-server/flask-site"

image_name="dijksterhuis/discogs-flask-server"
image_tag="dev"
container_name="pyserving-test"
networks="discogs-metadata-stores discogs-redis-site-queries"

docker run -d --rm -p 80:5000 -p 4040:4040 \
    -v $pth:/home/site \
    -w /home \
    --name $container_name \
        $image_name":"$image_tag

for net in networks ; do docker network connect $net $container_name ; done

docker exec -it $container_name /bin/ash -c "/home/site/main.py"
docker stop $container_name; docker rm $container_name