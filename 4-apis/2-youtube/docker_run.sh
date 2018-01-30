#!/bin/bash
docker stop discogs-youtube-api
docker rm discogs-youtube-api
docker run -di --restart=always -v logs:/logging --name discogs-youtube-api dijksterhuis/discogs-youtube-api:dev /bin/ash -c 'python youtube_api.py'
docker network connect --ip=172.25.0.3 discogs-external-apis discogs-youtube-api
docker network connect host discogs-youtube-api