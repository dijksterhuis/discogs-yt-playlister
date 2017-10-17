#!/bin/bash

###### labels restful flask api container

docker run -d --rm \
    --network rest-labels \
    -p 127.0.0.1:90:5000 \
    --name rest-api-mongo-labels \
    dijksterhuis/discogs-flask-mongo-api:test \
    /bin/ash -c 'python flask_mongo_queries_labels.py'

###### artists restful flask api container

docker run -d --rm \
    --network rest-artists \
    -p 127.0.0.1:91:5000 \
    --name rest-api-mongo-artists \
    dijksterhuis/discogs-flask-mongo-api:test \
    /bin/ash -c 'python flask_mongo_queries_artists.py'

###### masters restful flask api container

docker run -d --rm \
    --network rest-masters \
    -p 127.0.0.1:92:5000 \
    --name rest-api-mongo-masters \
    dijksterhuis/discogs-flask-mongo-api:test \
    /bin/ash -c 'python flask_mongo_queries_masters.py'



## testing
# curl -i -H "Content-Type: application/json" -X POST -d '{"id":"1"}' -v localhost:91/artists