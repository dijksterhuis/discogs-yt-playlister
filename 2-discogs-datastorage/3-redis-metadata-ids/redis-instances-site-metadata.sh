#!/bin/bash

docker network create discogs-metadata-stores

# ------------------------------------------------------------------
###### redis-metadata-unique
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 7100:6379 \
    -v redis-unique-tags:/data \
    --name redis-metadata-unique \
    --network discogs-metadata-stores \
    redis:alpine redis-server --appendonly yes