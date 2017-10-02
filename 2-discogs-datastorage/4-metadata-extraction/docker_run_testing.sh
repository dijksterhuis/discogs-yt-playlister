#!/bin/bash
docker run -it --rm \
    -v metadata-extraction-logs:/logging \
    --name discogs-metadataextraction-base \
    --network perm-metadata-stores \
    dijksterhuis/masters-metadata-extraction:testing \
    /bin/ash -c '/home/masters_metadata_recursive.py /home/jsons/discogs_20170901_masters.json --verbose'

#docker run -it --rm \
#    -v discogs-jsons:/home/jsons \
#    -v metadata-extraction-logs:/logging \
#    --name discogs-metadataextraction-joblib \
#    --link redis-metadata-master-ids \
#    masters-metadata-extraction:testing \
#    /bin/ash -c '/home/masters_metadata_joblib.py /home/jsons/discogs_20170901_masters.json --verbose'