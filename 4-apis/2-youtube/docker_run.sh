#!/bin/bash
docker stop discogs-youtube-api
docker rm discogs-youtube-api
docker run -di --restart=always -v logs:/logging --name discogs-youtube-api dijksterhuis/discogs-youtube-api:dev
docker network connect --ip=172.25.0.2 discogs-external-apis discogs-youtube-api
docker network connect host discogs-youtube-api