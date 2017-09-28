#!/bin/bash
#-v $path/testing/:/home/xmls \
#path=$(pwd)

docker run -it --rm \
    -v discogs-db-xmls:/home/xmls \
    -v discogs-db-jsons:/home/jsons \
    -w /home/ \
    --name discogs-xml2json2mongo \
    --link discogs-jsons \
    discogs-xml2json2mongo:test \
    /bin/bash -c ./convert_and_load.sh
#    /bin/bash -c ./convert_to_json.sh
