pth="/home/dijksterhuis/Documents/discogs-yt-playlister/3-discogs-site/1-py-server"

docker run -it --rm -p 80:5000 -p 4040:4040 \
    -v $pth:/home/site \
    -w /home \
    --network discogs-redis-site-queries \
    --name pyserving-test \
    dijksterhuis/discogs-flask-server:dev /bin/ash