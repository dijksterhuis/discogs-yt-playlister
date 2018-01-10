# Discogs DB Dataget

A Web App to generate private playlists on Youtube from the [discogs monthly data dumps](http://data.discogs.com/).

Go here to try it out: [http://bec48fd6.ngrok.io/](http://bec48fd6.ngrok.io/)

## Build Info - V1 (Python ETL)

Basic premise:

1. Download xml dump files
2. Load into Mongo DB instances
3. Extract the necessary data from Mongo DBs into Redis query instances
4. Redis instances accesible from webserver via static IP RESTful APIs
5. Query data (video urls) cached in Redis
6. Webserver for Youtube OAuth2 per User session
7. RESTful API for Youtube API call to create a private playlist for User (TODO)
8. Nginx and uwsgi serving the flask application (TODO - lack of SSL / HTTPS breaks the oauth flow)

Originally this was meant to be prototyped with Redis, but I ended up having so much fun with it I fell into the Redis rabbit hole. For a final production version of the webapp, a SQL/Hadoop system might want to be implemented.


### 1-discogs-dataget
### 1-downloads  - 0.0.5
Curls the required files, pipes output to gzip, writes xml to disk (docker volume `discogs-db-xmls`). Only needs to run once a month to get new files (DB exports uplaoded monthly - usually 1st of month).

### 2-discogs-datastorage
#### 1-mongo
`mongo-instances-docker-run.sh` starts several mongo-db instances for storing the discogs data files in pure JSON (document) format

Script doc string:
- Sets up a network for all the databses, create individual docker volumes for each instance and start the instances
- To use:
  - 1. Pass the following as arguments set up mongodb instances for all files:
  ```bash
  ./test.sh labels releases masters artists
  ```
  - 2. Or pass one/two of the above to start a single instance:
  ```bash
  ./test.sh labels
  ./test.sh labels releases
  ```
  
#### 2-xmls2mongo
Take the files from `discogs-db-xmls`, parse with `xmltodict` & load each document into seperate mongo instances per discogs file

#### 3- redis-metadata-ids
Sets up redis instances for caches, hashes, queryable data and site metadata
Redis performed MUCH faster than MongoDB on benchmark tests (redis circa 2 seconds with intersections in python between 3 redis dbs, MongoDB minimum 5 seconds, depending on size of query)

#### 6- redis-ETL
Take necessary data from mongo db collections, import into redis instances.

### 3-discogs-site
All code for serving the site

#### 1-py-serving
Flask server that handles the query building & api logic

#### x-nginx
TODO Nginx + uwsgi server

### 4-apis
RESTful APIs the webserver connects to Redis instances through