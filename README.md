# Discogs DB Dataget

A Web App to generate private playlists on Youtube from the [discogs monthly data dumps](http://data.discogs.com/).

## Build Info - V1 (Python ETL)

Basic premise:
1. Download xml dump files
2. Flatten xmls
3. Load into Mongo DB instances
4. Extract the necessary data from Mongo DBs into Redis query instances (this should really be API based!)
5. Run a query on site - GET data request through RESTful APIs from Redis instances
6. Store cache of query data (video urls) in redis
7. Perform OAuth connection for User session to Youtube
8. Send video urls to Youtube to create a provate playlist for user


TODOs:
- Data is initially kept in mongo DB instances for redundancy purposes. This data dump files can be quite big. This may change in future (Added processing steps which don't otherwise add much use).
- MongoDB APIs - single document (misc analysis) / full collection (redis load) queries

### 1-discogs-dataget
#### 1-downloads  - 0.0.5
- Only needs to run once a month to get new files (DB exports uplaoded monthly - usually 1st of month)
- Does the following actions:
  - Curls the required files (uploaded in a "discogs\_"$yearmonth"01\_"$filename".xml.gz" format) from discogs data dump site
  - Pipe curl output to gzip
  - Write xml to disk (docker volume discogs-db-xmls)
- Dockerfile has a CMD command as of version 0.0.5

TODOs:
- download\_xmls.sh: What if the data is not uploaded on the 01 of the month? It isn't always!
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
- Take the files from discogs-db-xmls
- Parses xmls with xmltodict python library
- Loads each document (entity) using pymongo import
- Lots of ETL going on here - flattening the nested dictionaries & renaming keys mostly
- docker\_run.sh file is set up with a CMD so is executable

TODOs:
- Dockerfile: Create an entrypoint so can test different ETL scripts 
- Dockerfile: Docker build-then-run script so don't have to keep changing this file - how to do version number? Jenkins?
- mongo_ETL.py: Data files don't necessarily upload on 01 of month.
  - input: /home/xmls/discogs_20170901_masters.xml
  - expected output: masters
  - line affected: collection_choice = infile.split('01_')[1].split('.xml')[0]
  - solution: Need to do some form of regex that matches the numbers from 20170101_ and splits
- mongo_ETL.py: Is all the releases data covered?
- mongo_ETL.py: If the releases file, only keep certain elements to save memory usage (mongo eats it up on my 16GB box) (This needs checking!):
  - release id
  - release title
  - main_release
  - label id
  - release date
  - companies - id, entity type / desc ?
  - extra artists ?
  - artists ?
  - country ?

#### 3- redis-metadata-ids
- sets up redis instances for caches, hashes, queryable data and site metadata

TODOs:
- AUTOMATE!!!

#### 6- redis-ETL
The big bonanza... Take necessary data from mongo db collections, import into redis instances.
Lots going on here... TO UPDATE...

TODO:
- THERE MUST BE AN EASIER WAY!

### 3-discogs-site
#### 1-get-metadata-redis
- no docker image built yet (not needed for testing)
- tester to get some video files
- should be used for the webpage logic

## Build Info - V2 (Hadoop Ecosystem)
- This is a "data product" (existing data will be used to generate more data - economic feedback model)
- So could be argued that it should live on the hadoop ecosystem
- Possible to parse xml files with Apache Pig


## UI notes
### Filters
#### Random searches
These masters filters could primarily be used to filter down results. But, that means forcing users to *know* what they are searching for first.
A better option is including ALL filter choices together.
E.g. Artist search (with aliases) then also filter by year and style

- Masters file (currently have):
  - Year
  - Genre
  - Style

- Masters file (could use):
  - Artists
  - Data Quality

- Releases file:
  - Format (vinyl etc.)
  - Country 
  - Release DATE (yy-mm-dd)
  - Companies involved + their entity type (pressed by, recorded at)

- Artists file:
  - Possible linking to secondary artist names (aliases)

- Labels file:
  - Possible linking to sublabels

#### Specific choices
- All videos for specified / list of EITHER:
  - artist
  - label
  - release
  
- THIS IS WHAT REDIS WAS BUILT FOR!
- This is a simple search query, can include auto-complete example
  - Find a specfic key (i.e. "James Holden")
  - Return all the master ids for this search
  - Then can use other filtering methods if required (year, include aliases etc.)
  
Data model:

3x databases (artist, label, release)
Keys: entity name
Values: master ids

#### Query Results

- Currently only outputting list of youtube videos
- Need a better results output
- With other metadata, could do a per entity results summary e.g.
  - Label name : number of results
  - Artist name : number of results
- This would allow for further fine tuning of filtering

## JSON notes
### Masters
- Main release refers to the "main" release for the master in the releases json data.
- There are several releases per master, but only one of them is a "main" release.
- Doesn't have an 'ID' json attribute, is a tag of each element:
```xml
<master id="18500">
```
- Need to find a way to extract this!! DONE via xmltodict library

### Releases
- Doesn't have an 'ID' json attribute.
- Must be a tag of each elelemt - ```<master id="18500">```
- Need to find a way to extract this!!
```xml
<release id="1" status="Accepted">
```