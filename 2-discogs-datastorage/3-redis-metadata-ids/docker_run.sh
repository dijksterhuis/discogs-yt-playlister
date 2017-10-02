#!/bin/bash
# append dbs - storing the actual key value data
# this could change to a more appropriate db instead of redis

docker run -d --rm -p 6379:6379 \
    -v redis-perm-master-ids:/data \
        --name redis-metadata-master-ids \
            --network perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

docker run -d --rm -p 6380:6379 \
    -v redis-unique-tags:/data \
        --name redis-metadata-unique \
            --network perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

docker run -d --rm -p 6381:6379 \
    -v redis-videos-by-id:/data \
        --name redis-videos-masters \
            --network perm-metadata-stores \
                redis:alpine redis-server --appendonly yes

# buffer dbs - storing session data
# docker run -d --rm -p 6400:6379 -v redis-metadata:/data --name redis-session-query redis:alpine
