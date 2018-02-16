## TODOs

- Applications DDoS
  - Count of videos API?
    - Disallow if original master IDs search volumes are > MAX_VIDEOS
      - Estimate max set cards? - meh.
      - replace smembers - there's a redis command for limits on sets, isn't there?
  - Webserver / API Timeouts
  - Stuff?

- Generate new access tokens
  - All open branches to pull from master (remove old tokens)

- Setup linux box (again)
  - ngrok
  - API access keys
  - public IP ?
  - public domain name for nginx ?

- Update README!

- !!! RELOAD RELEASES DATA INTO MONGO

- country data
  - load

- how to do main site query loading efficiently?

- log to logging docker volume
  - Mongo load
  - Site usage

- Code clean up!
  - MyLogger Redis Inserts:
    - TODO Not happy about logs being inside redis insert funcs
    - needs too many variables...
  - non alphanumeric redis inserts:
    - clean the data?
    - include or exclude?
    - some labels do have symbols in names! (they're hip like that)

- autocomplete-inserts branch:
    - change query autocomplete to UPPER in main.py
    - deploy + test!
  
- Exception handling

- Documentation
  - What instnaces hold what data
  - where data is used
  - glossary of terms

- Change around IP addresses of Youtbue API and webserver

- Youtube API - how to thread video addition requests?

- NGINX + USWGI
  - ??? https://stackoverflow.com/questions/27920852/nginx-ssl-inside-a-docker-container
  - https://hub.docker.com/r/zerossl/client/
  - Nginx config set up nerd out...
  - Build own ? 2 container method preffered (nginx scaling)
  - How to SSL it ?
    - oauth breaks using tiangulo docker image.
  - Any other options ?
  
- Autocomplete on text searches:
  - jQuery - helper function so simple 'artist' or 'label' func where applicable.
  - Reformat redis Text to UPPER:Original ?
  - How many many results to display ? Dynamic in Redis API ?
  - Don't forget data is in Discogs format - e.g. Artefakt (2)

- discogs api:
  - lists
  - collection
  - wantlist

- Playlist creation
  - add to existing playlists?
  - Manage existing youtube playlists?
    - All playlists or only one user has added via discogs-yt
      - Requires holding user data!

- Build query (intersections) on seperate RESTful API ?

- Release date filtering:
  - Release dates are really dirty!!!
  - Design release date query logic (Y & M & D set intersection? or YYYY-MM choice in redis?)
  - Rerun mongo releases script (updated date logic)
  - Run release date redis inserts
  - Add release date query fields

- Redis Inserts:
  - Check how Redis handles multiple I/O requests ?
    - Load to DB 1, switch DB 0 to DB 1, then flush DB 1 after inserts ? 
  - Updates !?
    - Currently assume a master title/label won't change. It could!

- `download_xmls.sh`
  - How to log/automate a flag if the md5checksum results aren't right?
  - What if the data is not uploaded on the 01 of the month? It isn't always!
    - Run a batch job every day checking for a file?
    - No xml file exists, quit, else download?
    - Need to look at curl usage/html response from incorrect address...

- Jenkins CI

- Finish styling:
  - bootstrap?
  - Smaller buttons!
  - Remove / change nav links?
  - Font
    - More aesthetically pleasing size ratios (Dynamic ?)
    - Nicer font choice!
  - Design responsiveness?
  - Calendar for date queries?
  - Lighter back colour for inputs
  - Turn off autocomplete suggestions from browser

- FAQ / Landing / Welcome / Privacy Policy pages - started

- Query Javascript loading query script... Give the user something to look at?

- **REAL** artist names ?
  - Covering all of an artists aliases...
  - Requires artists file + linking to masters file...
  - Don't forget names are in Discogs format...

- Hadoop w/ Hive / SQL implementation ?

- MongoDB APIs
  - misc analysis RESTful APIs (public?)
  - convert redis inserts to api requests?
  - yields with requests? request generator syntax?

- Mongo Inserts
  - Does data need to be kept in Mongo ? Do straight ETL ?
  - Database name should be something relevant to file's date information e.g. `179` for `20170901`
    - how to pass on to Redis inserts?
  - Data files don't necessarily upload on `01` of month.
  - Does releases data fit into 10GB of memeory?
    - 8 million records = 42% memory usage (0.42 * 15.6 = 6.5 GB...)
    - Mongo version is 3.4
    - So SHOULD default to WiredTiger enginer
    - Shouldn't use more than 50% system memory?

## Completed

- autocomplete:
  - javascript
    - AJAX / JQuery...
      - <https://jqueryui.com/autocomplete/>
      - <http://flask.pocoo.org/docs/0.12/patterns/jquery/>
      - <https://stackoverflow.com/questions/15310644/flask-ajax-autocomplete>
  - redis APIs
  - Lexographical queries:
    - **NOT FUCNTIONING CORRECTLY**:
      - 'James Hol' returns James Hollingworth **ONLY** -> no James Holden! Must be Redis API lexigraphical search code issue.
- SessionID logic
  - not randint!
  - Max query API...


- Requests timeouts - requests.get('http://github.com', timeout=0.001)
- Youtube API
  - Playlist gen
  - Video additions
    - Is POST request with no response data possible?
    - Will "/playlist\_added.html" load?
- MONGO > REDIS ETL ERRORS:
  - This should not be inserted as a list! Should extract each value and insert them...
- log to logging docker volume...
  - Redis ETL
- Redis inserts:
  - Sorted set logic for autocomplete searches
- Are redis ID -> name instances needed?! -> No, marked as depreciated