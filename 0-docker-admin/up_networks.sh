#!/bin/bash

docker network create --driver bridge --subnet=172.23.0.0/16 --internal --attachable discogs-get-apis
docker network create --driver bridge --subnet=172.18.0.0/16 --internal --attachable discogs-mongo
docker network create --driver bridge --subnet=172.20.0.0/16 --internal --attachable discogs-redis-autocomplete
docker network create --driver bridge --subnet=172.24.0.0/16 --internal --attachable discogs-redis-caches
docker network create --driver bridge --subnet=172.19.0.0/30 --internal --attachable discogs-redis-site-queries