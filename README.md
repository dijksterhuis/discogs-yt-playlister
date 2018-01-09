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

General TODOs:
- Data is initially kept in mongo DB instances for redundancy purposes. This data dump files can be quite big. This may change in future (Added processing steps which don't otherwise add much use).
- Jenkins CI

### 1-discogs-dataget
#### 1-downloads  - 0.0.5
Curls the required files, pipes output to gzip, writes xml to disk (docker volume `discogs-db-xmls`). Only needs to run once a month to get new files (DB exports uplaoded monthly - usually 1st of month).


TODOs:
- `download_xmls.sh`: What if the data is not uploaded on the 01 of the month? It isn't always!
  - Run a batch job every day checking for a file?
  - No xml file exists, quit, else download?
  - Need to look at curl usage/html response from incorrect address...

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

TODOs:
None! Yay!

#### 2-xmls2mongo
Take the files from `discogs-db-xmls`, parse with `xmltodict` & load each document into seperate mongo instances per discogs file

TODOs:
- Database name should be something relevant to file's date information e.g. `179` for `20170901`
- Data files don't necessarily upload on `01` of month.

#### 3- redis-metadata-ids
Sets up redis instances for caches, hashes, queryable data and site metadata
Redis performed MUCH faster than MongoDB on benchmark tests (redis circa 2 seconds with intersections in python between 3 redis dbs, MongoDB minimum 5 seconds, depending on size of query)

#### 6- redis-ETL
Take necessary data from mongo db collections, import into redis instances.

TODO:
- Change to a SQL or Hadoop DB location? Redis is getting complicated with the number of DBs

### 3-discogs-site
All code for serving the site
#### 1-py-serving
Flask server that handles the query building & api logic

#### x-nginx
TODO Nginx + uwsgi server

TODOs:
- Build query (intersections) on seperate RESTful API
- Nginx + uwsgi server (SSL/HTTPS currently breaks the oauth flow)

### 4-apis
RESTful APIs the webserver connects to Redis instances through

TODOs:
- Build query (intersections) on seperate RESTful API
- Build youtube data on seperate RESTful API (POST request with no return response?)
- Clear videos cache for session id
- MongoDB APIs - single document (misc analysis) public RESTful APIs