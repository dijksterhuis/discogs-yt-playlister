#!/bin/bash

# ------------------------------------------------------------------
###### redis-hash-ids
### N.B. Cannot store multiple videos in hash values --- single attributes
# relevant search hashes for all files
# to be used for autocomplete / searching
## hash index: id type (release ?, label, master ?, artist)
## fields: name (value: James Holden) , id (value: 119429)

docker run -d --rm -p 6379:6379 \
    -v redis-hash-ids:/data \
        --name redis-hash-ids \
            --network discogs-redis-querying \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-masters-ids
# relevant search sets for master release titles
# to be used for autocomplete / searching
## keys: release-title
## values: master-id

#docker run -d --rm -p 6379:6379 \
#    -v redis-masters-ids:/data \
#        --name redis-masters-ids \
#            --network discogs-redis-querying \
#                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-artists-ids
# relevant search sets for master artists
# to be used for autocomplete / searching
## keys: artist-name
## values: artist-id

#docker run -d --rm -p 6378:6379 \
#    -v redis-artists-ids:/data \
#        --name redis-artists-ids \
#            --network discogs-redis-querying \
#                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-filtering
# sets of ids with year, genre, style etc. tags as indexes
# to be used for filtering searches / searching for all data
# pulled from master file only!
# TODO release date (from releases)

docker run -d --rm -p 6380:6379 \
    -v redis-metadata-filtering:/data \
        --name redis-metadata-filtering \
            --network discogs-redis-querying \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-unique
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only
# TODO release date (from releases)

docker run -d --rm -p 6381:6379 \
    -v redis-unique-tags:/data \
        --name redis-metadata-unique \
            --network discogs-perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-video-id-urls
# video urls by master id
# the actual urls to be sent through the youtube API
## key: master-id , values: urls (http://www.youtube.com/etc.etc.)

docker run -d --rm -p 6382:6379 \
    -v redis-videos-masters:/data \
        --name redis-videos-masters \
            --network discogs-perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-query-cache
# store the session results that a user has confirmed for query
# store video ids as sets per user session (delete key once sent to youtube)

docker run -d --rm -p 6383:6379 \
    -v redis-session-query-cache:/data \
        --name redis-query-cache \
            --network discogs-redis-caches \
                redis:alpine redis-server

# buffer dbs - storing session data
# docker run -d --rm -p 6400:6379 -v redis-metadata:/data --name redis-session-query redis:alpine
