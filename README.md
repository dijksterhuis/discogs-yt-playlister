## Discogs DB Dataget
------------------------------------------------------------------------
### 1-discogs-dataget
------------------------------------------------------------------------

#### 1-downloads  - 0.0.4

- filename changed for https://github.com/philipmat/discogs-xml2db
- The discogs-db-dls container
- Does:
  - Curl the required files
  - Pipe curl output to gzip
  - Write xml to disk (volume discogs-db-xmls)

#### 2-Gunzip (DEPRECIATED)

- Was going to do the archiving after getting the files
- But, do we really need to keep EVERY SINGLE file?
- Can do, leaving a build folder for it in case
- But the 1-downloads method of curl piped to gzip seems sensible

#### 3-xmltojson - 0.0.4 - DEPRECIATED

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

#### 1-mongo

- a mongo db instance for storing jsons files (is this needed?)

#### 2-xmls2mongo

- Take the files from discogs-db-jsons
- Parses as and loads one by one using pymongo import

#### 3- redis-metadata-ids

- sets up a persistant (append file) redis instance for master ids by tags
- TODO - add a new redis db for all unique tags for loading into the site

#### 4-metadata-extraction - testing

- extract tags, videos and master ids to load into the redis metadata db
- have two versions, both need testing and comparing against each other:
  - recursive:
    - takes around 1 hour to complete
    - recurses through the json objects looking for tags
    - is slow, but will ALWAYS find the tags if it exists
  - joblib:
    - multiple threads with a list comp
    - should be faster, but memory intensive? could be a resource error
    - TODO - NEED to implement the recursive stuff for this

------------------------------------------------------------------------
### 3-discogs-site
------------------------------------------------------------------------


#### 1-get-metadata-redis

- no docker image built yet (not needed for testing)
- tester to get some video files
- should be used for the webpage logic


------------------------------------------------------------------------
### UI notes
------------------------------------------------------------------------

#### Filters

##### Random searches

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

##### Specific choices

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