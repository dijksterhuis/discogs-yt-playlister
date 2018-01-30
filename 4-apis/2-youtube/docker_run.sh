#!/bin/bash
docker stop discogs-youtube-api
docker rm discogs-youtube-api
docker run -di --restart=always --net=host -v logs:/logging --name discogs-youtube-api dijksterhuis/discogs-youtube-api:dev
docker network connect discogs-external-apis discogs-youtube-api