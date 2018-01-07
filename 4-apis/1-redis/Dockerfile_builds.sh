#!/bin/bash

# build and run all images / run scripts in lower directories
cwd=$(pwd)
pth=/home/dijksterhuis/Documents/discogs-yt-playlister/4-apis/1-redis
cd $pth

for file in * ; \
    do \
        if [ -d $file ] ; \
            then \
                mv -v 'DEV_api_build_funx.py' $file'/api_build_funx.py' ; \
                echo 'Building and running: '$file ; \
                docker-build-contextual $file ; \
                chmod u+x $file'/docker_run.sh' ; \
                ./$file'/docker_run.sh' ; \
        fi ; \
    done
    
cd $cwd