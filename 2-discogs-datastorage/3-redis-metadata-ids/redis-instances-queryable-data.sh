#!/bin/bash

docker network create discogs-redis-site-queries

# ------------------------------------------------------------------
###### redis-masters-ids
# relevant search sets for master release titles
# to be used for autocomplete / searching
## keys: release-title
## values: master-id
docker run -d --rm -p 7000:6379 \
    -v redis-masters-ids:/data \
    --name redis-masters-ids \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-artists-ids
# relevant search sets for master artists
# to be used for autocomplete / searching
## keys: artist-name
## values: artist-id
docker run -d --rm -p 7001:6379 \
    -v redis-artists-ids:/data \
    --name redis-artists-ids \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-mastersid-artistname
# relevant search sets for checking which master releases user wants (against relevant artists)
# to be used for autocomplete / searching
## keys: masters_id
## values: artist_name
docker run -d --rm -p 7002:6379 \
    -v redis-mastersid-artistname:/data \
    --name redis-mastersid-artistname \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-mainrel-masterid
# main relase > masters id mapping (for labels processing...)
## keys: main_release id
## values: masters_id
docker run -d --rm -p 7003:6379 \
    -v redis-mainrel-masterid:/data \
    --name redis-mainrel-masterid \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-video-id-urls
# video urls by master id
# the actual urls to be sent through the youtube API
## key: master-id , values: urls (http://www.youtube.com/etc.etc.)
docker run -d --rm -p 7004:6379 \
    -v redis-videos-masters:/data \
    --name redis-video-id-urls \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-filtering
# sets of ids with year, genre, style etc. tags as indexes
# to be used for filtering searches / searching for all data
# pulled from master file only!
# TODO release date (from releases)
docker run -d --rm -p 7005:6379 \
    -v redis-metadata-filtering:/data \
    --name redis-metadata-filtering \
    --network discogs-redis-site-queries \
    redis:alpine redis-server --appendonly yes
