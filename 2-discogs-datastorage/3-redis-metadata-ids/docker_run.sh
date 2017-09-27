#!/bin/bash
docker run -d --rm -p 6379:6379 -v redis-metadata:/data --name redis-metadata-master-ids redis:alpine redis-server --appendonly yes
#docker run -d --rm -p 6379:6379 -v redis-metadata:/data --name redis-metadata-master-ids redis:alpine
