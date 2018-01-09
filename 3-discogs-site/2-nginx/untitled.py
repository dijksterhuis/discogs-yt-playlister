#!/bin/bash

docker run -di -p 127.0.0.1:80:80 -p 127.0.0.1:443:443 --name discogs-nginx discogs-nginx-proxy:dev
docker network connect discogs-web-serve discogs-nginx