# general imports
import json, os, datetime, time, redis, requests
from random import randint
#from werkzeug.datastructures import ImmutableOrderedMultiDict

# site imports
from flask import  Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug import generate_password_hash, check_password_hash

# Google imports
from youtube_playlist_gen import create_playlist, insert_videos
import googleapiclient.discovery
import google_auth_oauthlib.flow
import google.oauth2.credentials

#TODO import google.oauth2.credentials <<<<<- This breaks it?!

# --------------------------------------------------
# Flask vars
# --------------------------------------------------

# Flask App
app = Flask(__name__)

# Super secret cookie session key
app.secret_key = os.urandom(24)

# --------------------------------------------------
# Google api vars
# --------------------------------------------------

# https://developers.google.com/youtube/v3/quickstart/python#further_reading

CLIENT_SECRETS_FILE = "/app/client_secrets.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# --------------------------------------------------
# My vars
# --------------------------------------------------

# reldate?
BASE_API_URL = 'http://172.23.0.'
TAGS = ['year','genre','style']
API_URLS = { \
				'unique_metadata' : BASE_API_URL+'6/unique_metadata' \
				, 'ids_from_name' : BASE_API_URL+'3/get_ids_from_name' \
				, 'ids_from_metadata' : BASE_API_URL+'5/ids_from_metadata' \
				, 'video_urls' : BASE_API_URL+'4/video_urls' \
				, 'video_query_cache' : BASE_API_URL+'7/video_query_cache' \
				, 'video_query_cache_clear' : BASE_API_URL+'7/video_query_cache_clear' \
				, 'max_query_id' : BASE_API_URL+'7/max_query_id' \
			}

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

def api_get_requests(host_string, r_json=None):
	api_call_headers = {"Content-Type": "application/json"}
	if r_json != None:
		r = requests.get( host_string , json = r_json , headers = api_call_headers)
	else:
		r = requests.get( host_string )
	r_data = r.json()
	if isinstance(r_data,bytes) or isinstance(r_data,bytearray) or isinstance(r_data,str):
		output = json.loads(r_data)
	else:
		output = r_data
	return output

def api_put_requests(host_string, r_json):
	api_call_headers = {"Content-Type": "application/json"}
	r = requests.put( host_string , json = r_json , headers = api_call_headers)
	r_data = r.json()
	if isinstance(r_data,bytes) or isinstance(r_data,bytearray) or isinstance(r_data,str):
		output = json.loads(r_data)
	else:
		output = r_data
	return output

def redis_host(value):
	return redis.Redis(host=value,port=6379)

# --------------------------------------------------
# server logic
# --------------------------------------------------

<<<<<<< HEAD
@app.route('/',methods=['GET'])
def index():
	return redirect('home')

@app.route('/welcome',methods=['GET'])
=======
@app.route('/home',methods=['GET'])
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up
def home():
	if 'credentials' not in session: return redirect('authorize')
	return redirect(url_for('/query_builder'))

<<<<<<< HEAD
@app.route('/query_builder',methods=['GET','POST'])
=======

@app.route('/',methods=['GET','POST'])
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up
#@login_required
#@subscription_required
def query():
	
	if 'credentials' not in session: return redirect('authorize')
		
	if request.method == 'GET':
		print('GET',request)
		
		uniq_params = { tag : api_get_requests(API_URLS['unique_metadata'], {'tag':tag} ) for tag in TAGS }
		return render_template('/query-form.html',years=uniq_params['year'],genres=uniq_params['genre'],styles=uniq_params['style'])
	
	elif request.method == 'POST':
		print('POST',request)
		
		# ---- Query parameters
		
		wide_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in TAGS}
		artist_name = request.form.get('search:artist_name', type=str, default='')
		release_name = request.form.get('search:release_name', type=str, default='')
		label_name = request.form.get('search:label_name', type=str, default='')
		
		# ---- Get master IDs from APIs
		
		artist_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'artist','name':artist_name} )
		release_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'release','name':release_name} )
		#label_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'label','name':release_name} )
		master_ids_dict = api_get_requests(API_URLS['ids_from_metadata'], wide_query_dict )
		
		# ---- Calculate Query (TODO move off to a seperate API ?)
		
		wide_query_sets = list_of_sets(master_ids_dict.values())
		
		if len(wide_query_sets) == 0:
			to_intersect = [artist_ids,release_ids]
		else:
			to_intersect = [artist_ids,release_ids,set.intersection(*wide_query_sets)]
		
		master_ids = list(set.intersection( *list_of_sets(to_intersect) ))
		
		# ---- Get video urls
		
		all_links = api_get_requests(API_URLS['video_urls'], {'master_ids': master_ids} )
		numb_links = len(all_links)
		if numb_links == 0:
			return render_template('/no-results.html')
		
		# ---- Add to redis cache
		
		redis_query_cache_adds = api_put_requests( \
													API_URLS['video_query_cache'] \
													, { 'session_id' : session['session_id'] , 'video_ids': all_links } \
												)
		if 'numb_videos' not in session.keys():
			session['numb_videos'] = numb_links
		else:
			session['numb_videos'] += numb_links
		return render_template('/videos_added.html',intersex=all_links,total_count=numb_links)

@app.route('/current_urls',methods=["GET"])
def current_vids():
	return redirect(url_for('/query_builder'))

@app.route('/authorize',methods=['GET'])
def authorize():
	
	session['session_id'] = 'query:'+str(randint(0,1000))
	
	print(session['session_id'])
	
	# https://developers.google.com/youtube/v3/quickstart/python#further_reading
	
	# Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
	# steps.
	
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
	flow.redirect_uri = url_for('oauth2callback', _external=True)
	
	# This (access_type) parameter enables offline access which gives your application
	# both an access and refresh token.
	# This parameter (include_granted_scopes) enables incremental auth.
	
	authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
	
	# Store the state in the session so that the callback can verify that
	# the authorization server response.
	
	session['state'] = state
	
	return redirect(authorization_url)


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
									
	return redirect(url_for('query'))

@app.route('/create_playlist',methods=['GET','POST'])
def send_to_yt():
	
	if 'credentials' not in session: return redirect('authorize')
	
	if request.method == 'GET':
		video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
		return render_template('/playlist_details.html' , numb_videos = len(video_ids))
		
	if request.method == 'POST':
		
		title, desc = request.form.get('playlist_title'), request.form.get('playlist_desc')
		
		# https://developers.google.com/youtube/v3/quickstart/python#further_reading
		
		# Load the credentials from the session.
		credentials = google.oauth2.credentials.Credentials(**session['credentials'])
		client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
		video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
		video_ids = [ video_id.lstrip('https://www.youtube.com/watch?v=') for video_id in video_ids]
		playlist_result = create_playlist(client, title, desc)
		
		responses = dict()
		for idx, video_id in enumerate(video_ids):
			responses[str(idx)] = { 'video_id' : video_id }
			try:
				responses[str(idx)] = { 'video' : insert_videos(client, playlist_result , video_id ) }
			except:
				responses[str(idx)] = { 'video' : 'NOT ADDED' }
				
		#clear_cache = api_get_requests(API_URLS['video_query_cache_clear'], {'session_id' : session['session_id']} )
		#session.clear()
		
		# wait 5 seconds so youtube updates...
		
		time.sleep(5)
		
		return render_template( '/playlist_added.html' \
										, pl_title=title, pl_desc=desc, pl_link=playlist_result['id'], first_vid=video_ids[0] )

if __name__ == '__main__':
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	app.run(host='0.0.0.0',debug=True,port=80)
	#app.run(host='0.0.0.0',debug=False,port=80)