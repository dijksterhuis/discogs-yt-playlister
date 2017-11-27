#!/bin/bash

#docker run -dt --restart=always \
#    -v discogs-labels-mongo-conf:/home \
#        -v discogs-labels-mongo-data:/data/db \
#            --network discogs-mongo \
#                --name mongo-discogs-labels \
#                    mongo

#docker run -dt --restart=always \
#    -v discogs-artists-mongo-conf:/home \
#        -v discogs-artists-mongo-data:/data/db \
#            --network discogs-mongo \
#                --name mongo-discogs-artists \
#                    mongo

docker run -dt --restart=always \
    -v discogs-masters-mongo-conf:/home \
        -v discogs-masters-mongo-data:/data/db \
            --network discogs-mongo \
                --name mongo-discogs-masters \
                    mongo

docker run -dt --restart=always \
    -v discogs-releases-mongo-conf:/home \
        -v discogs-releases-mongo-data:/data/db \
            --network discogs-mongo \
                --name mongo-discogs-releases \
                    mongo