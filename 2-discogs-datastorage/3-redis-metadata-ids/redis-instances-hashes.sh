#!/bin/bash

# ------------------------------------------------------------------
###### redis-hash-ids
### N.B. Cannot store multiple videos in hash values --- single attributes
# relevant search hashes for all files
# to be used for autocomplete / searching
## hash index: id type (release ?, label, master ?, artist)
## fields: name (value: James Holden) , id (value: 119429)

#docker run -d --rm -p 7000:6379 \
#    -v redis-hash-ids:/data \
#        --name redis-hash-ids \
#            --network discogs-redis-querying \
#                redis:alpine redis-server --appendonly yes


