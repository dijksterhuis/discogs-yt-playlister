#!/bin/bash

docker run -it --net=host --rm \
    -v discogs-xmls:/home/downloads \
    -v discogs-xmlsold:/home/old_downloads \
    --name discogs-xml-downloads \
    discogs-db-dls:0.0.5