docker run -it --rm -p 80:5000 -p 4040:4040 \
    -v ~/Code/1-builds/discogs-yt-playlister/3-discogs-site/1-py-server/flask-site:/home/site \
        -w /home \
            --network perm-metadata-stores \
                --name pyserving \
                dijksterhuis/discogs-flask-server:dev /bin/ash