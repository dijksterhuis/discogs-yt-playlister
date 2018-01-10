## TODOs

- Downloads md5checksum
  - How to log/automate a flag if the checksum isn't right?

- Youtube API
  - Playlist gen
  - Video additions (is POST request with no return data possible? - will playlist\_added.html load?)

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

- Query Javascript loading query script... Give the user something to look at!

- **REAL** artist name ? Covering all of an artists aliases ?

- NGINX + USWGI
  - Nginx config set up nerd out...
  - Build own ? 2 container method preffered (nginx scaling)
  - How to SSL it ?
    - oauth breaks using tiangulo docker image.
  - Any other options ?