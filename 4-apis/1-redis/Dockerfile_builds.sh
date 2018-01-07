#!/bin/bash

# build and run all images / run scripts in lower directories

for file in * ; \
    do \
        if [ -d $file ] ; \
            then \
                git pull ; \
                docker-build-contextual './'$file ; \
                chmod u+x './'$file'/docker_run.sh' ; \
                './'$file'/docker_run.sh' \
        fi ; \
    done
