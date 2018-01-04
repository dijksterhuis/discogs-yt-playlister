#!/bin/bash
docker run \
    -it --rm \
    -v discogs-xmls:/home/xmls \
    --network discogs-mongo \
    --name discogs-pymongoimport \
    dijksterhuis/discogs-pymongoimport:0.9.0