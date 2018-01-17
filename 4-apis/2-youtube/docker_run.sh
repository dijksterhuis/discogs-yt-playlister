#!/bin/bash

docker run -di --restart=always --net=host -v logs:/logging --name discogs-youtube-api discogs-youtube-api:dev
docker network connect discogs-get-apis discogs-youtube-api