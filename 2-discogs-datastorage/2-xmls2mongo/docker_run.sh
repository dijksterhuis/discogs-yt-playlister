#!/bin/bash
docker run -it --rm \
    -v discogs-xmls:/home/xmls \
    --link mongo-discogs \
    --network mongo-json-access \
    --name discogs-pymongoimport \
    dijksterhuis/discogs-pymongoimport:0.1.0 \
    /bin/bash -c 'find /home/xmls -name \*.xml -exec /home/convert_xmls_2.py {} \;'
#     /bin/ash -c '/home/convert_xmls.py /home/xmls/discogs_20170901_masters.xml --verbose'
