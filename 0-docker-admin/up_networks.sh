#!/bin/bash
docker network create --driver bridge --subnet=172.23.0.0/16 discogs-get-apis
docker network create --driver bridge --subnet=172.25.0.0/16 discogs-external-apis
docker network create --driver bridge discogs-mongo
docker network create --driver bridge --subnet=172.20.0.0/16 discogs-redis-autocomplete
docker network create --driver bridge discogs-redis-caches
docker network create --driver bridge discogs-redis-site-queries
docker network create --driver bridge discogs-webserve
