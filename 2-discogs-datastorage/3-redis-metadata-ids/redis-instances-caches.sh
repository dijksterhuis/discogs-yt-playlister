#!/bin/bash

docker network create discogs-redis-caches

# ------------------------------------------------------------------
###### discogs-session-query-cache
# store the session results that a user has confirmed for query
# store video ids as sets per user session (delete key once sent to youtube)

docker run -d --rm -p 6401:6379 \
    -v discogs-session-query-cache:/data \
    --name discogs-session-query-cache \
    --network discogs-redis-caches \
    redis:alpine redis-server

# ------------------------------------------------------------------
###### redis-discogs-sessions
# store information about the user session

docker run -d --rm -p 6400:6379 \
    -v discogs-user-session-cache:/data \
    --name discogs-user-session-cache \
    --network discogs-redis-caches \
    redis:alpine
