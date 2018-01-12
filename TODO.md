## TODOs

- ERROR HANDLING!

- Playlist creation
  - add to existing playlists?

- Youtube API
  - Playlist gen
  - Video additions
    - Is POST request with no response data possible?
    - Will "/playlist\_added.html" load?

- Clear videos cache for session id after playlist build

- Build query (intersections) on seperate RESTful API ?

- Release date filtering:
  - Release dates are really dirty!!!
  - Design release date query logic (Y & M & D set intersection? or YYYY-MM choice in redis?)
  - Rerun mongo releases script (updated date logic)
  - Run release date redis inserts
  - Add release date query fields

- Country data
  - Acid Techno from Germany!

- Redis Inserts:
  - Sorted set logic for autocomplete searches
  - Check how Redis handles multiple I/O requests ?
    - Load to DB 1, switch DB 0 to DB 1, then flush DB 1 after inserts ? 
  - Updates !?
    - Currently assume a master title/label won't change. It could!

- Autocomplete on text searches:
  - javascript
    - AJAX / JQuery...
      - <https://jqueryui.com/autocomplete/>
      - <http://flask.pocoo.org/docs/0.12/patterns/jquery/>
      - <https://stackoverflow.com/questions/15310644/flask-ajax-autocomplete>
  - redis APIs
  - Lexographical queries:
    - Reformat redis Text to UPPER:Original ?
    - How many many results to display ?

- NGINX + USWGI
  - Nginx config set up nerd out...
  - Build own ? 2 container method preffered (nginx scaling)
  - How to SSL it ?
    - oauth breaks using tiangulo docker image.
  - Any other options ?

- `download_xmls.sh`
  - How to log/automate a flag if the md5checksum results aren't right?
  - What if the data is not uploaded on the 01 of the month? It isn't always!
    - Run a batch job every day checking for a file?
    - No xml file exists, quit, else download?
    - Need to look at curl usage/html response from incorrect address...

- Mongo Inserts
  - Does data need to be kept in Mongo ? Do straight ETL ?
  - Database name should be something relevant to file's date information e.g. `179` for `20170901`
    - how to pass on to Redis inserts?
  - Data files don't necessarily upload on `01` of month.
  - Does releases data fit into 10GB of memeory?
    - 8 million records = 42% memory usage (0.42 * 15.6 = 6.5 GB...)
    - Mongo version is 3.4
    - So SHOULD default to WiredTiger enginer
    - Shouldn't use more than 50% system memory!

- Jenkins CI

- Finish styling:
  - bootstrap?
  - Smaller buttons
  - Remove / change nav links?
  - Font
    - More aesthetically pleasing size ratios (Dynamic ?)
    - Nicer font choice!
  - Design responsiveness?
  - Calendar for date queries?
  - Lighter back colour for inputs
  - Turn off autocomplete suggestions from browser

- FAQ / Landing / Welcome page

- Privacy Policy

- Query Javascript loading query script... Give the user something to look at!

- **REAL** artist names ?
  - Covering all of an artists aliases...
  - Requires artists file + linking to masters file...

- Hadoop w/ Hive / SQL implementation ?

- MongoDB APIs - single document (misc analysis) public RESTful APIs