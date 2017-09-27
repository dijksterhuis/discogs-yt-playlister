#!/bin/bash
docker run -it --rm \
    -v discogs-xmls:/home/xmls \
    -v discogs-jsons:/home/jsons \
    -w /home/ \
    --name xml2json \
    discogs-xml2json:0.0.4 \
    /bin/ash -c 'find /home/xmls -name \*.xml -print -exec /home/convert_xmls.py {} --verbose \;'
