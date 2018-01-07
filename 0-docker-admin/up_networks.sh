docker network create --subnet=172.23.0.0/16 $api_net
docker network create discogs-redis-site-queries
docker network create discogs-metadata-stores
docker network create discogs-mongo
docker network create discogs-redis-autocomplete
docker network create discogs-redis-caches
docker network create discogs-redis-site-queries