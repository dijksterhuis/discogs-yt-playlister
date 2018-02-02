#!/bin/bash
containers='discogs-redis-autocomplete-label discogs-redis-autocomplete-release discogs-redis-autocomplete-artist redis-mastersid-labelname redis-labels-ids redis-metadata-unique-reldate redis-metadata-unique-year redis-metadata-unique-style redis-metadata-unique-genre redis-masters-ids redis-artists-ids redis-mastersid-artistname redis-mainrel-masterid redis-video-id-urls redis-masterids-titles discogs-user-customlist-cache discogs-user-wantlist-cache discogs-user-session-cache discogs-session-query-cache'

for container in $containers; do docker stop container ; docker rm container ; done

volumes='discogs-redis-autocomplete-artist discogs-redis-autocomplete-label discogs-redis-autocomplete-release discogs-session-query-cache discogs-user-customlist-cache discogs-user-session-cache discogs-user-wantlist-cache redis-artists-ids redis-labels-ids redis-mainrel-masterid redis-masterids-titles redis-masters-ids redis-mastersid-artistname redis-mastersid-labelname redis-metadata-filtering redis-metadata-unique-genre redis-metadata-unique-reldate redis-metadata-unique-style redis-metadata-unique-year redis-session-query-cache redis-unique-tags redis-video-id-urls redis-videos-masters'

for v in $volumes ; do docker volume rm $v ; done