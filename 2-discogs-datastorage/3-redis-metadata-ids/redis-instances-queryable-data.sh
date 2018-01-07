#!/bin/bash

network='discogs-redis-site-queries'
container_names='redis-masterids-titles redis-metadata-filtering redis-video-id-urls redis-mainrel-masterid redis-mastersid-artistname redis-artists-ids redis-masters-ids redis-metadata-unique-genre redis-metadata-unique-style redis-metadata-unique-year redis-metadata-unique-reldate'
port=7000
docker network create $network

for container_name in $container_names ; 
do \
    docker run \
        -d \
        --restart=always \
        -p $port:6379 \
        -v $container_name:/data \
        --name $container_name \
        --network $network \
        redis:alpine redis-server --appendonly yes ; \
    echo $container_name' started.' ;\
    $port=$(($port+1)) ;\
done


### NOTES:
# ----------------------------------------------------------------
###### redis-masters-ids
# ----------------------------------------------------------------
# relevant search sets for master release titles
# to be used for autocomplete / searching
## keys: release-title
## values: master-id
# ----------------------------------------------------------------
###### redis-artists-ids
# ----------------------------------------------------------------
# relevant search sets for master artists
# to be used for autocomplete / searching
## keys: artist-name
## values: artist-id
# ----------------------------------------------------------------
###### redis-mastersid-artistname
# ----------------------------------------------------------------
# relevant search sets for checking which master releases user wants (against relevant artists)
# to be used for autocomplete / searching
## keys: masters_id
## values: artist_name
# ----------------------------------------------------------------
###### redis-mainrel-masterid
# ----------------------------------------------------------------
# main relase > masters id mapping (for labels processing...)
## keys: main_release id
## values: masters_id
# ----------------------------------------------------------------
###### redis-video-id-urls
# ----------------------------------------------------------------
# video urls by master id
# the actual urls to be sent through the youtube API
## key: master-id , values: urls (http://www.youtube.com/etc.etc.)
# ----------------------------------------------------------------
###### redis-metadata-filtering
# ----------------------------------------------------------------
# sets of ids with year, genre, style etc. tags as indexes
# to be used for filtering searches / searching for all data
# pulled from master file only!
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-masterids-titles
# ----------------------------------------------------------------
## key: master-id , values: master release title
# ------------------------------------------------------------------
###### redis-metadata-unique-genre
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-style
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-year
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)
# ----------------------------------------------------------------
###### redis-metadata-unique-reldata (month???)
# ----------------------------------------------------------------
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)