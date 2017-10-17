#!/bin/bash

# ------------------------------------------------------------------
###### redis-hash-ids
# relevant search data for all files
# to be used for autocomplete / searching
## hash index: id type (release ?, label, master, artist)
## fields: name (value: James Holden) , id (value: 119429)

docker run -d --rm -p 6379:6379 \
    -v redis-hash-ids:/data \
        --name redis-hash-ids \
            --network redis-querying \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-metadata-filtering
# sets of ids with year, genre, style etc. tags as indexes
# to be used for filtering searches / searching for all data
# pulled from master file only!

docker run -d --rm -p 6380:6379 \
    -v redis-metadata-filtering:/data \
        --name redis-metadata-filtering \
            --network redis-querying \
                redis:alpine redis-server --appendonly yes


# ------------------------------------------------------------------
###### redis-metadata-unique
# for year, genre, style etc. tags to be pulled onto the site
# to be used for filtering searches / searching for all data
# pulled from master file only

docker run -d --rm -p 6381:6379 \
    -v redis-unique-tags:/data \
        --name redis-metadata-unique \
            --network perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-videos-masters
# video urls and name by master id
# the actual urls to be sent through the youtube API
## hash index: id (29048)
## fields: name (A Break In The Clouds) , url (value: http://www.youtube.com/etc.etc.)

docker run -d --rm -p 6382:6379 \
    -v redis-videos-masters:/data \
        --name redis-videos-masters \
            --network perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

# ------------------------------------------------------------------
###### redis-query-cache
# store the temp results that a user has confirmed for query
# store video ids as sets per user session (delete key once sent to youtube)

docker run -d --rm -p 6383:6379 \
    -v redis-session-query-cache:/data \
        --name redis-query-cache \
            --network redis-caches \
                redis:alpine redis-server

# buffer dbs - storing session data
# docker run -d --rm -p 6400:6379 -v redis-metadata:/data --name redis-session-query redis:alpine
