#!/bin/bash
docker stop discogs-nginx
docker rm discogs-nginx
docker run -di -p 127.0.0.1:70:80 -p 127.0.0.1:443:443 --network discogs-webserve --name discogs-nginx dijksterhuis/discogs-nginx-proxy:dev
