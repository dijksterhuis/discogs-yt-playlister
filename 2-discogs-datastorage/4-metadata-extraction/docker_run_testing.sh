#!/bin/bash
docker run -it --rm \
    -v discogs-jsons:/home/jsons \
    -v metadata-extraction-logs:/logging \
    --name discogs-metadataextraction-base \
    masters-metadata-extraction:testing \
    --link redis-metadata-master-ids \
    /bin/ash -c '/home/masters_metadata.py /home/jsons/discogs_20170901_masters.json --verbose'

docker run -it --rm \
    -v discogs-jsons:/home/jsons \
    -v metadata-extraction-logs:/logging \
    --name discogs-metadataextraction-joblib \
    masters-metadata-extraction:testing \
    --link redis-metadata-master-ids \
    /bin/ash -c '/home/masters_metadata_joblib.py /home/jsons/discogs_20170901_masters.json --verbose'