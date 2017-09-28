#!/bin/bash
#-v $path/testing/:/home/xmls \
#path=$(pwd)

docker run -it --rm \
    -v discogs-db-xmls:/home/xmls \
    -v discogs-db-jsons:/home/jsons \
    -w /home \
    --link discogs-jsons \
    --name discogs-xml2json2mongo \
    discogs-xml2json2mongo:0.0.1 \
    /bin/bash -c ./convert_and_load.sh