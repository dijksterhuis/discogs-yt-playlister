#!/bin/bash

docker network create discogs-metadata-stores

# ------------------------------------------------------------------
###### redis-metadata-unique-genre
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 7100:6379 \
    -v redis-metadata-unique-genre:/data \
    --name redis-metadata-unique-genre \
    --network discogs-metadata-stores \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-unique-style
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 7101:6379 \
    -v redis-metadata-unique-style:/data \
    --name redis-metadata-unique-style \
    --network discogs-metadata-stores \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-unique-year
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 7102:6379 \
    -v redis-metadata-unique-year:/data \
    --name redis-metadata-unique-year \
    --network discogs-metadata-stores \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-unique-reldata
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 7103:6379 \
    -v edis-metadata-unique-reldate:/data \
    --name redis-metadata-unique-reldate \
    --network discogs-metadata-stores \
    redis:alpine redis-server --appendonly yes