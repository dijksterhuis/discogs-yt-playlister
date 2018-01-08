#!/bin/bash

# build and run all images / run scripts in lower directories
cwd=$(pwd)
pth=/home/dijksterhuis/Documents/discogs-yt-playlister/4-apis/1-redis
cd $pth
echo "-------------------------------------------------"
echo 'Building api containers...'
echo "-------------------------------------------------"
for file in * ; \
    do \
        if [ -d $file ] ; \
            then \
                cp -v 'DEV_api_build_funx.py' $file'/api_build_funx.py' ; \
                echo 'Building: '$file ; \
                cd $file ; \
                docker-build-contextual ./ ; \
                cd $pth ; \
        fi ; \
    done
echo "-------------------------------------------------"
echo 'Starting api containers...'
echo "-------------------------------------------------"
./prod_docker_run.sh
echo "-------------------------------------------------"
echo 'End of script...'
echo "-------------------------------------------------"
cd $cwd