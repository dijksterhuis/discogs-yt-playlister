#!/bin/bash

while getopts p:e:r:c option
do
    case "${option}"
        in
        p) PATH=${OPTARG};;
        e) EXTENSION=${OPTARG};;
        r) RUN_COMAND=${OPTARG};;
        c) CPUS=${OPTARG};;
    esac
    
    function parallel_jobs {
        if [ $CPUS -z ] ; \
        then \
            TOTAL_CPUS=$(getconf _NPROCESSORS_ONLN) ; \
            if [ $TOTAL_CPUS > 2 ] ; \
            then CPUS=$(($total_cpus-2)) ; \
            else CPUS=1 ; \
            fi ; \
        fi
    
        find $PATH -print0 -name \*.$EXTENSION | xargs -0 --max-args=1 --max-procs=$cpus $RUN_COMMAND
    }

    paths="./2-discogs-datastorage/6-redis-ETL/1-searches/ ./2-discogs-datastorage/6-redis-ETL/2-autocomplete/"
    cwd=$(pwd)
    echo "------------------------------------------------"
    echo " --- Starting redis ETL script -----------------"
    echo "------------------------------------------------"
    cd $HOME"/discogs-yt-playlister/"
    for pth in $paths ; do parallel_jobs -p $pth -e "sh" -c "/bin/bash -c" ; done
    cd $cwd
done