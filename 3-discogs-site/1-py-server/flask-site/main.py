# general imports
import json, os, datetime, time, redis, requests
#from werkzeug.datastructures import ImmutableOrderedMultiDict

# site imports
from flask import  Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug import generate_password_hash, check_password_hash


# Google imports
from youtube_playlist_gen import create_playlist, insert_videos
import googleapiclient.discovery
import google_auth_oauthlib.flow


#TODO import google.oauth2.credentials <<<<<- This break it?!

# --------------------------------------------------
# Flask vars
# --------------------------------------------------

# Flask App
app = Flask(__name__)

# Super secret cookie session key
app.secret_key = generate_password_hash(os.urandom(24))

# --------------------------------------------------
# Google api vars
# --------------------------------------------------

CLIENT_SECRETS_FILE = "client_secrets.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# --------------------------------------------------
# misc functions
# --------------------------------------------------

def api_get_requests(host_string, r_json):
	api_call_headers = {"Content-Type": "application/json"}
	r = requests.get( host_string , json = r_json , headers = api_call_headers)
	r_data = r.json()
	if isinstance(r_data,bytes) or isinstance(r_data,bytearray) or isinstance(r_data,str):
		output = json.loads(r.json())
	else:
		output = r.json()
	return output

def redis_meta_host(value):
	return redis.Redis(host='redis-metadata-unique-'+value,port=6379)

def redis_host(value):
	return redis.Redis(host=value,port=6379)

def get_redis_values(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

def get_redis_keys(redis_instance):
	return [i.decode('utf-8') for i in list(redis_instance.keys())]

# --------------------------------------------------
# server logic
# --------------------------------------------------

@app.route('/home',methods=['GET'])
def home():
	if 'credentials' not in flask.session:
		return redirect('authorize')
	
	return render_template('/no_results.html')

@app.route('/',methods=['GET','POST'])
#@login_required
#@subscription_required
def query():
	if 'session_id' not in flask.session:
		flask.session['session_id'] = os.urandom(24)
		
	if request.method == 'GET':
		print('GET',request)
		
		# reldate?
		tags = ['year','genre','style']
		uniq_params = { tag : api_get_requests('http://172.23.0.6/unique_metadata', {'tag':tag} ) for tag in tags }
		return render_template('/query-form.html',years=uniq_params['year'],genres=uniq_params['genre'],styles=uniq_params['style'])
	
	## These can be big queries...
	
	elif request.method == 'POST':
		
		print('POST',request)
		
		time_dict = { 0: ('start_time',datetime.datetime.now() ) }
		
		wide_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in ['year','genre','style']}
		print(wide_query_dict)
		
		artist_name = request.form.getlist('search:artist_name')[0]
		release_name = request.form.getlist('search:release_name')[0]
		label_name = request.form.getlist('search:label_name')[0]
		
		print(artist_name,release_name,label_name)
		
		# -------- ids from names API
		
		artist_ids = api_get_requests('http://172.23.0.3/get_ids_from_name', {'name_type':'artist','name':artist_name} )
		release_ids = api_get_requests('http://172.23.0.3/get_ids_from_name', {'name_type':'release','name':release_name} )
		#label_ids = api_get_requests('http://172.23.0.3/get_ids_from_name', {'name_type':'label','name':release_name} )
		
		print(artist_ids,release_ids) #, label_ids
		
		time_dict[1] = ('wide_query_dict_get' , datetime.datetime.now())
		
		print('getting: ',wide_query_dict)
		
		if len(wide_query_dict) != 0:
			master_ids_dict = api_get_requests('http://172.23.0.5/ids_from_metadata', wide_query_dict )
			time_dict[2] = ('metadata ids set' , datetime.datetime.now())
			print('master ids gotten')
			intersections = set.intersection(*[set(i) for i in master_ids_dict.values() if len(i) > 0])
			time_dict[3] = ('intersection_time_delta' , datetime.datetime.now())
		else:
			intersections = set()
			
		# ---- TODO - and/or logic - intersections
		
		print('intersections gotten')
		
		# ---- TODO - and/or logic - unions
		
		lets_union_u = [artist_ids, release_ids, intersections]
		if sum([len(i) for i in lets_union_u]) != 0:
			unions = list(set.union( *[set(i) for i in lets_union_u if len(i) > 0] ))
		else:
			return render_template('/no_results.html')
		time_dict[4] = ('union_time_delta' , datetime.datetime.now())
		print('unions gotten')
		
		print('total master ids to get videos for: ',len(unions))
		
		# ---- VIDEOS GET
		
		all_links = api_get_requests('http://172.23.0.4/video_urls', {'master_ids': unions} )
			
		print('videos gotten')
		
		time_dict[5] = ('videos_time_delta' , datetime.datetime.now())
		tot = len(all_links)
		print(all_links)
		
		# ---- TIMINGS TEST OUTPUT
		
		print('\ntimings: key, time since start, time since last op, str_key')
		for time_key,time_value in time_dict.items():
			if time_key is 0:
				print(time_key  , 0 , 0  , time_value[0] )
			else:
				from_start = time_value[1] - time_dict[0][1]
				from_last_op = time_value[1] - time_dict[time_key-1][1]
				print(time_key , from_start , from_last_op , time_value[0] )
		total_time = datetime.datetime.now() - time_dict[0][1]
		print('\ntotaltime',total_time.total_seconds())
		print('\n')
		
		# TODO API + SESSION!!!
		session_id = 1
		
		redis_query_cache_adds = sum( [ redis_host('discogs-session-query-cache').sadd(session_id, \
													link.replace('https://youtube.com/watch?v=','') ) for link in all_links ] )
		redis_host('discogs-session-query-cache').expire(session_id,30*60)
		
		return render_template('/added.html',intersex=all_links,total_count=tot)


@app.route('/authorize',methods=['GET'])
def authorize():
	
	# Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
	# steps.
	
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
	flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
	
	# This (access_type) parameter enables offline access which gives your application
	# both an access and refresh token.
	# This parameter (include_granted_scopes) enables incremental auth.
	
	authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
	
	# Store the state in the session so that the callback can verify that
	# the authorization server response.
	
	flask.session['state'] = state
	
	return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
	
	# Specify the state when creating the flow in the callback so that it can
	# verify the authorization server response.
	
	state = flask.session['state']
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
	flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
	
	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	
	authorization_response = flask.request.url
	flow.fetch_token(authorization_response=authorization_response)
	
	# Store the credentials in the session.
	# ACTION ITEM for developers:
	#     Store user's access and refresh tokens in your data store if
	#     incorporating this code into your real app.
	
	credentials = flow.credentials
	flask.session['credentials'] = { \
										'token': credentials.token \
										, 'refresh_token': credentials.refresh_token \
										, 'token_uri': credentials.token_uri \
										, 'client_id': credentials.client_id \
										, 'client_secret': credentials.client_secret \
										, 'scopes': credentials.scopes \
									}
									
	return flask.redirect(flask.url_for('/query_builder'))


@app.route('/create_playlist',methods=['GET'])
def send_to_yt():
	if 'session_id' not in flask.session:
		return redirect('query_builder')
	
	title = request.form.get('playlist_title')
	desc = request.form.get('playlist_desc')
	
	#session_id = flask.session['session_id']
	session_id = 1
	
	# Load the credentials from the session.
	#credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
	
	#client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
	
	r = redis_host('discogs-session-query-cache')
	video_ids = list(r.smembers(session_id))
	
	playlist_result = create_playlist(client, title, desc)
	for video_id in video_ids:
		insert_videos(client, playlist_result , video_id)

if __name__ == '__main__':
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	app.run(host='0.0.0.0',debug=True,port=80)
	#app.run(host='0.0.0.0',debug=False,port=80)