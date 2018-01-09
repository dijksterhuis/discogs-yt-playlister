#!/bin/bash

docker run -di -p 127.0.0.1:80:80 -p 127.0.0.1:443:443 --network discogs-web-serve --name discogs-nginx dijksterhuis/discogs-nginx-proxy
