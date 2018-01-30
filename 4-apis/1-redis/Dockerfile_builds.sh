#!/bin/bash

# build and run all images / run scripts in lower directories
cwd=$(pwd)
pth=/home/ec2-user/discogs-yt-playlister/4-apis/1-redis
cd $pth
echo "-------------------------------------------------"
echo 'Building api containers...'
echo "-------------------------------------------------"
echo 'Building: base image'
docker-build-contextual ./0-base/
for file in * ; \
    do \
        if [ -d $file ] && [ $file != '0-base' ] ; \
            then \
                echo "-------------------------------------------------"
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