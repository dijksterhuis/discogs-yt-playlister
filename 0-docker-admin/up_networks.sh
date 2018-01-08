#!/bin/bash

docker network create --driver bridge discogs-get-apis
docker network create --driver bridge discogs-mongo
docker network create --driver bridge discogs-redis-autocomplete
docker network create --driver bridge discogs-redis-caches
docker network create --driver bridge discogs-redis-site-queries