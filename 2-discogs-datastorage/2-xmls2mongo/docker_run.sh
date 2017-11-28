#!/bin/bash
docker run -it --rm \
    -v discogs-xmls:/home/xmls \
    --network discogs-mongo \
    --name discogs-pymongoimport \
    dijksterhuis/discogs-pymongoimport:0.1.0 \
    /bin/ash -c 'find /home/xmls -name \*.xml -exec /home/convert_xmls_2.py {} \;'
#     /bin/ash -c '/home/convert_xmls.py /home/xmls/discogs_20170901_masters.xml --verbose'
