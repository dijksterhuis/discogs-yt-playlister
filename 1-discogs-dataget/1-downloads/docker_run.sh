#!/bin/bash

docker run -it --net=host --rm \
    -v discogs-xmls:/home/downloads \
    -v discogs-xmlsold:/home/old_downloads \
    -w /home \
    --name discogs-xml-downloads \
    discogs-db-dls:0.0.4 \
    /bin/ash -c ./download_xmls.sh