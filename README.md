## Discogs DB Dataget
------------------------------------------------------------------------
------------------------------------------------------------------------
### 1-discogs-dataget
------------------------------------------------------------------------

##### 1-downloads  - 0.0.4

- filename changed for https://github.com/philipmat/discogs-xml2db
- The discogs-db-dls container
- Does:
  - Curl the required files
  - Pipe curl output to gzip
  - Write xml to disk (volume discogs-db-xmls)

##### 2-Gunzip (DEPRECIATED)

- Was going to do the archiving after getting the files
- But, do we really need to keep EVERY SINGLE file?
- Can do, leaving a build folder for it in case
- But the 1-downloads method of curl piped to gzip seems sensible

##### 3-xmltojson - 0.0.4 - DEPRECIATED

- No point storing the jsons if they're accesible from mongo
  - Loading files into python requires a lot of memeory and io
  - Extracting from mongo is much less resource intensive
- Takes the xml files in discogs-db-xmls docker volume
- Converts to json using https://github.com/philipmat/discogs-xml2db
  - N.B. THIS IS HACKY!
  - Pipes the std output into a "json" file
    - The "json" file doesn't have begin and end curly brackets
    - There is a "Parse x files as per your command" at the end of each file
  - There is an issue with the library - json\_exporter module doesn't load properly ?!?!
    - Needs to be fixed - raise an issue on github?
  

------------------------------------------------------------------------
### 2-discogs-datastorage
------------------------------------------------------------------------

##### 1-mongo

- a mongo db instance for storing jsons files (is this needed?)

##### 2-xmls2mongo

- Take the files from discogs-db-jsons
- Parses as and loads one by one using pymongo import

##### 3- redis-metadata-ids

- sets up a persistant (append file) redis instance for master ids by tags

##### 4-metadata-extraction - testing

- extract tags, videos and master ids to load into the redis metadata db
- have two versions:
  - base:
    - processes with single thread
    - will be slow, but releiable?
  - joblib:
    - multiple threads with a list comp
    - should be faster, but memory intensive? could be a resource error

------------------------------------------------------------------------
### 3-discogs-site
------------------------------------------------------------------------


##### 1-get-metadata-redis

- no docker image built yet (not needed for testing)
- tester to get some video files
- should be used for the webpage logic

------------------------------------------------------------------------
#### JSON notes
------------------------------------------------------------------------

##### Masters
- Main release refers to the "main" release for the master in the releases json data.
- There are several releases per master, but only one of them is a "main" release.
- Doesn't have an 'ID' json attribute.
- Must be a tag of each element - 
```xml
<master id="18500">
```
- Need to find a way to extract this!!

##### Releases
- Doesn't have an 'ID' json attribute.
- Must be a tag of each elelemt - ```<master id="18500">```
- Need to find a way to extract this!!
```xml
<release id="1" status="Accepted">
```