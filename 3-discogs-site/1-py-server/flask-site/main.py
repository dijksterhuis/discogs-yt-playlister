from __future__ import print_function
# general imports
import json, os, datetime, time, requests
from random import randint
#from werkzeug.datastructures import ImmutableOrderedMultiDict


import sys

# site imports
from flask import  Flask, render_template, redirect, url_for, request, session, flash, jsonify, make_response
from werkzeug import generate_password_hash, check_password_hash

# google imports
import google_auth_oauthlib.flow

# --------------------------------------------------
# Google api vars
# --------------------------------------------------

# https://developers.google.com/youtube/v3/quickstart/python#further_reading

CLIENT_SECRETS_FILE = "/home/site/client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# --------------------------------------------------
# Flask vars
# --------------------------------------------------

# Flask App
app = Flask(__name__)

# Super secret cookie session key
app.secret_key = os.urandom(24)

# --------------------------------------------------
# My vars
# --------------------------------------------------

VIDEO_LIMIT = 1000
BASE_API_URL = 'http://172.23.0.'
EXT_API_URL = 'http://172.25.0.'
#AUTO_API_URL = 'http://172.x.0.'
TAGS = ['year','genre','style']
NAME_FIELDS = ['artist','release','label']
NAV = \
            { \
                'Authorise' : '/authorise' \
                ,'Build A Query' : '/query_builder' \
                ,'FAQ' : '/faq' \
                ,'Current Videos' : '/current_urls' \
                , 'De-Authorise' : '/deauthorise'
            }
API_CALL_HEADERS = \
            { \
                "Content-Type": "application/json"\
            }
API_URLS = \
            { \
                'unique_metadata' : BASE_API_URL+'6/unique_metadata' \
                , 'ids_from_name' : BASE_API_URL+'3/get_ids_from_name' \
                , 'ids_from_metadata' : BASE_API_URL+'5/ids_from_metadata' \
                , 'video_urls' : BASE_API_URL+'4/video_urls' \
                , 'video_query_cache' : BASE_API_URL+'7/video_query_cache' \
                , 'video_query_cache_clear' : BASE_API_URL+'7/video_query_cache_clear' \
                , 'video_query_cache_max' : BASE_API_URL+'7/max_query_id' \
                , 'max_query_id' : BASE_API_URL+'7/max_query_id' \
                , 'playlist_creator' : EXT_API_URL+'3/create_playlist' \
                , 'video_adder' : EXT_API_URL+'3/insert_videos' \
                , 'auto_comp_names' : BASE_API_URL+'10/' \
            }
AUTOCOMPLETE_URLS = \
            { \
                'artist' : BASE_API_URL+'10/artist' \
                , 'release' : BASE_API_URL+'10/release' \
                , 'label' : BASE_API_URL+'10/label' \
            }
AD_STRING = '\n\nGenerated with discogs-youtube-playlister.com'

# --------------------------------------------------
# misc functions
# --------------------------------------------------

class timer:
    def __init__(self):
        #import datetime
        self.start = datetime.datetime.now()
    def time_taken(self):
        c_time = datetime.datetime.now() - self.start
        return c_time.total_seconds()

def list_of_sets(in_data):
    return [set(i) for i in in_data if len(i) > 0]

def set_from_dict(d):
    return set.intersection(*list_of_sets(d.values()))

def json_check(r_data):
    if isinstance(r_data,bytes) or isinstance(r_data,bytearray) or isinstance(r_data,str):
        output = json.loads(r_data)
    else:
        output = r_data
    return output

def api_get_requests(host_string, r_json=None):
    if r_json != None: r = requests.get( host_string , json = r_json , headers = API_CALL_HEADERS)
    else: r = requests.get( host_string )
    if r.status_code == 200:
        r_data = r.json()
        return json_check(r_data)
    else:
        flash('GET API issue. Please raise a bug report (TODO).','message')
        return jsonify(['GET API issue. Please raise a bug report (TODO).'])

def api_put_requests(host_string, r_json):
    r = requests.put( host_string , json = r_json , headers = API_CALL_HEADERS)
    r_data = r.json()
    return json_check(r_data)

def api_post(host_string, r_json):
    try:
        r = requests.post( host_string , json = r_json , headers = API_CALL_HEADERS , verify=False, timeout=(3.05,1))
    except:
        return 'No response object for this query'
    return True

# --------------------------------------------------
# server logic
# --------------------------------------------------

@app.route('/',methods=['GET'])
def index():
    return redirect('welcome')

@app.route('/welcome',methods=['GET'])
def home():
    return render_template('/welcome.html', nav_links=NAV)

@app.route('/_query_autocomplete')
def query_autocomplete():
    
    search, target = request.args.get('search'), request.args.get('target')
    results = api_get_requests(API_URLS['auto_comp_names'] + target, r_json = { 'value' : search } )
    output = jsonify(results['search_results'])
    return output

@app.route('/query_builder',methods=['GET','POST'])
def query_builder():
    
    if 'credentials' not in session: return redirect('authorise')
    
    #if 'session_id' not in session: session['session_id'] = 'query:'+str(randint(0,1000))
    
    if 'session_id' not in session: session['session_id'] = api_get_requests(API_URLS['video_query_cache_max'])['query']
    
    if request.method == 'GET':
        
        uniq_params = { tag : api_get_requests(API_URLS['unique_metadata'], {'tag':tag} ) for tag in TAGS }
        
        return render_template('/query-form.html' \
                                        , nav_links=NAV \
                                        , years=uniq_params['year'] \
                                        , genres=uniq_params['genre'] \
                                        , styles=uniq_params['style'] \
                                )
    
    elif request.method == 'POST':
        
        # ---- Query parameters
        
        metadata_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in TAGS}
        names = {name : request.form.get('search:'+name+'_name', type=str, default='') for name in NAME_FIELDS}
        
        if sum([len(v) for v in names.values()]) == 0:
            flash('You must provide an input for at least one text search field (Artist, Release or Label name).','message')
            return redirect(url_for('query_builder'))
        
        # ---- Get master IDs from APIs
        
        name_ids = { \
                        name : api_get_requests( \
                                                    API_URLS['ids_from_name'] \
                                                    , { 'name_type' : name, 'name' : names[name] } \
                                                ) \
                        for name in NAME_FIELDS \
                    }
        
        if sum([len(v) for v in name_ids.values()]) == 0:
            flash('No results found for your text input. Please try another search.','message')
            return redirect(url_for('query_builder'))
        
        # ---- Calculate Intersections (TODO move off to a seperate API ?)
        
        name_intersections = set_from_dict(name_ids)
        
        if sum([len(v) for v in metadata_query_dict.values()]) != 0:
            metadata_ids = api_get_requests(API_URLS['ids_from_metadata'], metadata_query_dict )
            metadata_intersections = set_from_dict(metadata_ids)
            master_ids = set.intersection(name_intersections,metadata_intersections)
        else:
            master_ids = name_intersections
        
        if len(master_ids) == 0:
            flash('No discogs master releases found for your query.','message')
            return redirect(url_for('query_builder'))
        
        # ---- Get video urls
        
        all_links = api_get_requests(API_URLS['video_urls'], {'master_ids': list(master_ids) } )
        numb_links = len(all_links)
        
        if numb_links == 0:
            flash("No videos found - but found Discogs releases. Some releases don't have any video links :(" ,'message')
            return redirect(url_for('query_builder'))
        
        elif numb_links > VIDEO_LIMIT:
            
            flash(\
                        'Too many videos in query. You have ' \
                        + str(numb_links)+' in your playlist. Playlist limit is ' \
                        + str(VIDEO_LIMIT)+ '.' \
                        ,'message' \
                    )
            
            return redirect(url_for('query_builder'))
        
        else:
            
            # ---- Add to redis cache
            
            redis_query_cache_adds = api_put_requests( \
                                                        API_URLS['video_query_cache'] \
                                                        , { 'session_id' : session['session_id'] , 'video_ids': all_links } \
                                                    )
            
            session['numb_videos'] = len( api_get_requests( \
                                                                API_URLS['video_query_cache'] \
                                                                , { 'session_id' : session['session_id'] } \
                                                            ))
            
            flash(str(numb_links)+' video links found. '+str(session['numb_videos'])+' unique videos in your playlist.','message')
            
            return redirect(url_for('query_builder'))

@app.route('/current_urls',methods=["GET"])
def current_vids():
    
    if 'credentials' not in session or 'session_id' not in session: return redirect('query_builder')
    
    if 'numb_videos' not in session:
        flash("You haven't added any videos yet, please find some to add before trying to view a list of them." ,'message')
        return redirect(url_for('query_builder'))
    
    video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
    
    return render_template('/videos_added.html' \
                                    , nav_links=NAV \
                                    , intersex=video_ids \
                                    , latest_count=len(video_ids) \
                                    , total_count=session['numb_videos'] \
                            )

@app.route('/faq',methods=["GET"])
def faq():
    return render_template('/faq.html', nav_links=NAV)

@app.route('/authorise',methods=['GET'])
def authorise():
    
    if 'credentials' in session:
        flash("You've already signed into a YouTube account. Click 'Deauthorise' in the Nav. Menu to sign into a new one.",'message')
        return redirect(url_for('query_builder'))
    
    # https://developers.google.com/youtube/v3/quickstart/python#further_reading
    
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    # "access_type" enables offline access which gives your application both an access and refresh token.
    # "include_granted_scopes" enables incremental auth.
    
    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
    
    # Store the state in the session so that the callback can verify that the authorization server response.
    
    session['state'] = state
    
    return redirect(authorization_url)

@app.route('/deauthorise',methods=['GET'])
def deauthorise():
    flash('You have deauthorised the YouTube account. Please authorise another account to use the service.','message')
    session.clear()
    return redirect('welcome')

@app.route('/oauth2callback')
def oauth2callback():
    
    # https://developers.google.com/youtube/v3/quickstart/python#further_reading
    
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    
    credentials = flow.credentials
    session['credentials'] = { \
                                'token': credentials.token \
                                , 'refresh_token': credentials.refresh_token \
                                , 'token_uri': credentials.token_uri \
                                , 'client_id': credentials.client_id \
                                , 'client_secret': credentials.client_secret \
                                , 'scopes': credentials.scopes \
                            }
    
    return redirect(url_for('query_builder'))

@app.route('/create_playlist',methods=['GET','POST'])
def send_to_yt():
    
    if 'credentials' not in session or 'session_id' not in session: return redirect('query_builder')
    
    if request.method == 'GET':
        
        video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
        
        # ---- TODO playlist management?
        # - add to an existing playlist?
        # - delete from playlists?
        
        return render_template('/playlist_details.html' \
                                        , nav_links=NAV \
                                        , numb_videos = len(video_ids)\
                                )
    
    if request.method == 'POST':
        
        title = request.form.get('playlist_title',type=str,default='Discogs Playlist')
        desc = request.form.get('playlist_desc',type=str,default='') + AD_STRING
        
        # ---- get video list
        
        video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
        video_ids = [ video_id.lstrip('https://www.youtube.com/watch?v=') for video_id in video_ids]
        
        # ---- create a playlist
        
        playlist_result = api_get_requests(API_URLS['playlist_creator'], r_json = { \
                                                                                'credentials' : session['credentials'] \
                                                                                , 'title' : title \
                                                                                , 'description' : desc \
                                                                            } )
        # ---- add videos to playlist (time out after 3 + 3 seconds)
        
        api_post(API_URLS['video_adder'], r_json = { \
                                                        'credentials' : session['credentials'] \
                                                        , 'playlist_id' : playlist_result['id'] \
                                                        , 'video_ids' : video_ids \
                                                    } )
        
        session.pop('session_id')
        #clear_cache = api_get_requests(API_URLS['video_query_cache_clear'], {'session_id' : session['session_id']} )
        
        if desc.rstrip(AD_STRING) == "": desc = "No description given."
        else: desc = desc.rstrip(AD_STRING)
        
        return render_template('/playlist_added.html' \
                                        , nav_links = NAV \
                                        , pl_title = title \
                                        , pl_desc = desc \
                                        , pl_link = playlist_result['id']\
                                        , first_vid = video_ids[0] \
                                        , test = playlist_result \
                                )

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0',debug=True,port=80)