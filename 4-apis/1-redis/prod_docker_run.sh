#!/bin/bash

# variable declarations

tags='ids-from-names video-urls-from-ids ids-from-metadata-filt form-metadata video-cache'
api_net='discogs-get-apis'
redis_site_net='discogs-redis-site-queries'
redis_cache_net='discogs-redis-caches'
# 172.23.0.2 is reserved for pyserving
ip_suffix=3
ip_prefix='172.23.0.'
numb_containers=$(echo $tags | wc -w)

# container logic

function bring_up_container {
    
    container_name='discogs-get-'$tag
    image='dijksterhuis/discogs-flask-redis-api:'$tag
    
    docker stop $container_name ; docker rm $container_name
    
    docker run -di --restart=always -v logs:/logging --name $container_name $image
    echo $container_name' started.'
    
    # MUST SPECIFY IP ADDRESSES ON NETWORK FOR REQUESTS
    docker network connect --ip=$ip_prefix$ip_suffix $api_net $container_name
    
    if [ $tag = 'video-cache' ] ; \
        then \
            docker network connect $redis_cache_net $container_name ; \
            echo $container_name' connected to networks '$api_net' & '$redis_cache_net'.' ; \
        else \
            docker network connect $redis_site_net $container_name ; \
            echo $container_name' connected to networks '$api_net' & '$redis_site_net'.' ; \
    fi
    
    
    echo $container_name' UP.'
    ip_suffix=$(($ip_suffix+1))
}

# script logic

for tag in $tags ; \
    do bring_up_container ; \
done

