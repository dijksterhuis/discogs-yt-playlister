#!/bin/bash
volumes='discogs-masters-mongo-data discogs-releases-mongo-data discogs-artists-mongo-data discogs-labels-mongo-data'
for v in $volumes ; do docker volume rm $v ; done