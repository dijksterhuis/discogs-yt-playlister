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
                cd $file ; \
                docker-build-contextual ./ ; \
                chmod u+x 'docker_run.sh' ; \
                './docker_run.sh' ; \
                cd $pth ; \
        fi ; \
    done
    
cd $cwd