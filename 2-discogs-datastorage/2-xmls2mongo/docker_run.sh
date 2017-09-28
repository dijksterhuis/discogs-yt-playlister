#!/bin/bash
docker run -it --rm \
    -v discogs-xmls:/home/xmls \
    --link discogs-mongo \
    --name discogs-pymongoimport \
    discogs-pymongoimport:0.0.3 \
    /bin/ash -c '/home/convert_xmls.py /home/xmls/discogs_20170901_masters.xml --verbose'
#    /bin/bash -c 'find /home/xmls -name \*.xml -exec /home/convert_xmls.py {} \;'