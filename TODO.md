## TODOs

- Youtube API
  - Playlist gen
  - Video additions (is POST request with no return data possible? - will playlist\_added.html load?)

- Clear videos cache for session id after playlist build

- Build query (intersections) on seperate RESTful API

- Release date filtering:
  - Design release date query logic (Y & M & D set intersection? or YYYY-MM choice in redis?)
  - Rerun mongo releases script (updated date logic)
  - Run release date redis inserts
  - Add release date query fields

- Labels Data:
  - TEST redis loads
  - Add labels API

- Country data - Acid Techno from Germany!

- Redis Inserts:
  - TEST new Mongo + Redis conn functions, Data insert functions
  - Sorted set logic for autocomplete searches
  - Switch databases on inserts ? Check how Redis handles multiple I/O requests ?

- `download_xmls.sh`
  - How to log/automate a flag if the md5checksum results aren't right?
  - What if the data is not uploaded on the 01 of the month? It isn't always!
    - Run a batch job every day checking for a file?
    - No xml file exists, quit, else download?
    - Need to look at curl usage/html response from incorrect address...

- Mongo Inserts
  - Does data need to be kept in Mongo ? Do straight ETL ?
  - Database name should be something relevant to file's date information e.g. `179` for `20170901` - how to pass on to Redis inserts?
  - Data files don't necessarily upload on `01` of month.
  - Does releases data fit into 10GB of memeory?

- Jenkins CI

- Autocomplete on text searches:
  - node.js
  - redis APIs
  - Lexographical queries:
    - Reformat redis Text to UPPER:Original ? 
    - How many many results to display ?

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

- FAQ / landing page

- Privacy Policy

- Query Javascript loading query script... Give the user something to look at!

- **REAL** artist name ? Covering all of an artists aliases ?

- Hadoop w/ Hive or SQL implementation?

- NGINX + USWGI
  - Nginx config set up nerd out...
  - Build own ? 2 container method preffered (nginx scaling)
  - How to SSL it ?
    - oauth breaks using tiangulo docker image.
  - Any other options ?

- MongoDB APIs - single document (misc analysis) public RESTful APIs