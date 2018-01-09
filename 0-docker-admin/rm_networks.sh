networks='discogs-get-apis discogs-redis-site-queries discogs-mongo discogs-redis-autocomplete discogs-redis-caches discogs-redis-site-queries'

for net in $networks ; 
do \
    docker network rm $net ; \
done