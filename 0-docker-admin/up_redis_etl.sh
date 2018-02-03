#!/bin/bash


function parallel_jobs {
    if [ $2 -z ] ; \
    then \
        if [ $(getconf _NPROCESSORS_ONLN) > 1 ] ; \
        then \
            cpus=$(getconf _NPROCESSORS_ONLN)-1 ;\
        else \
            cpus=$(getconf _NPROCESSORS_ONLN) ; \
        fi \
    else ; \
        cpus=$2 ; \
    fi
    
    find $1 -print0 -name \*.sh | xargs -0 --max-args=1 --max-procs=$cpus /bin/bash -c

}

paths="6-redis-ETL/1-searches/ 6-redis-ETL/2-autocomplete/"
cwd=$(pwd)
echo "------------------------------------------------"
echo " --- Starting redis ETL script -----------------"
echo "------------------------------------------------"
cd $HOME"/discogs-yt-playlister/"
for path in $paths ; do parallel_jobs $path ; done
cd $cwd