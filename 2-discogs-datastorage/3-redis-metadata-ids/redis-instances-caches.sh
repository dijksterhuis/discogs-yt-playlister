#!/bin/bash

docker network create discogs-redis-caches

# ------------------------------------------------------------------
###### redis-query-cache
# store the session results that a user has confirmed for query
# store video ids as sets per user session (delete key once sent to youtube)

docker run -d --rm -p 6401:6379 \
    -v redis-session-query-cache:/data \
    --name redis-query-cache \
    --network discogs-redis-caches \
    redis:alpine redis-server

# ------------------------------------------------------------------
###### redis-discogs-sessions
# store information about the user session

docker run -d --rm -p 6400:6379 \
    -v redis-discogs-sessions:/data \
    --name discogs-redis-caches \
    redis:alpine
