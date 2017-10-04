#!/bin/bash
#docker run -dt --restart=always -p 28002:27017 --name discogs-mongo -v discogs-jsons-conf:/home -v discogs-jsons-db:/data/db mongo:3.2
#docker run -dt --restart=always -p 90:8080 --name discogs-mongo-rest --link discogs-mongo:mongodb softinstigate/restheart:3.0.3

docker run -dt --restart=always -p 28002:27017 \
    -v discogs-jsons-conf:/home \
        -v discogs-jsons-db:/data/db \
            --network perm-metadata-stores \
            --network mongo-json-access \
                --name mongo-discogs \
                    mongo

#docker run -dt --restart=always -p 90:8080 \
#    --name restheart-mongo-discogs \
#        --link mongo-discogs \
#            softinstigate/restheart
