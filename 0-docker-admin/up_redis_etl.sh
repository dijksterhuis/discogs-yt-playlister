#!/bin/bash


function parallel_jobs {
    if [ $2 -z ] ; \
    then \
        total_cpus=$(getconf _NPROCESSORS_ONLN) ; \
        if [ $total_cpus > 2 ] ; \
        then cpus=$(($total_cpus-2)) ; \
        else cpus=1 ; \
        fi ; \
    else cpus=$2 ; \
    fi
    
    find $1 -print0 -name \*.sh | xargs -0 --max-args=1 --max-procs=$cpus /bin/bash -c

}

paths="./2-discogs-datastorage/6-redis-ETL/1-searches/ ./2-discogs-datastorage/6-redis-ETL/2-autocomplete/"
cwd=$(pwd)
echo "------------------------------------------------"
echo " --- Starting redis ETL script -----------------"
echo "------------------------------------------------"
cd $HOME"/discogs-yt-playlister/"
for path in $paths ; do parallel_jobs $path ; done
cd $cwd