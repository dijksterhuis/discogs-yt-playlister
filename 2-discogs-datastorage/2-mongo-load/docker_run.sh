#!/bin/bash

docker run -it --rm \
    -v discogs-jsons:/home/jsons \
    --link discogs-mongo \
    --name discogs-pymongoimport \
    discogs-pymongoimport:0.0.2 \
    /bin/bash -c 'find /home/jsons -name \*.json -exec /home/import_jsons.py {} \;'