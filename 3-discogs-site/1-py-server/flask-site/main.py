# general imports
import json, os, datetime, time, requests
from random import randint
#from werkzeug.datastructures import ImmutableOrderedMultiDict

# site imports
from flask import  Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug import generate_password_hash, check_password_hash

import os

#import google.oauth2.credentials
#import oauth2client
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
# 	https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
# 	https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

# --------------------------------------------------
# Google api vars
# --------------------------------------------------

# https://developers.google.com/youtube/v3/quickstart/python#further_reading

CLIENT_SECRETS_FILE = "/home/site/client_secrets.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Authorize the request and store authorization credentials.
def get_authenticated_service():
	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
	credentials = flow.run_console()
	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def print_response(response):
	print(response)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
	resource = {}
	for p in properties:
		# Given a key like "snippet.title", split into "snippet" and "title", where
		# "snippet" will be an object and "title" will be a property in that object.
		prop_array = p.split('.')
		ref = resource
		for pa in range(0, len(prop_array)):
			is_array = False
			key = prop_array[pa]
			
			# For properties that have array values, convert a name like
			# "snippet.tags[]" to snippet.tags, and set a flag to handle
			# the value as an array.
			if key[-2:] == '[]':
				key = key[0:len(key)-2:]
				is_array = True
			
			if pa == (len(prop_array) - 1):
				# Leave properties without values out of inserted resource.
				if properties[p]:
					if is_array:
						ref[key] = properties[p].replace('[','').replace(']','').split(',')
					else:
						ref[key] = properties[p]
			elif key not in ref:
				# For example, the property is "snippet.title", but the resource does
				# not yet have a "snippet" object. Create the snippet object here.
				# Setting "ref = ref[key]" means that in the next time through the
				# "for pa in range ..." loop, we will be setting a property in the
				# resource's "snippet" object.
				ref[key] = {}
				ref = ref[key]
			else:
				# For example, the property is "snippet.description", and the resource
				# already has a "snippet" object.
				ref = ref[key]
	return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
	good_kwargs = {}
	if kwargs is not None:
		for key, value in kwargs.items():
			if value:
				good_kwargs[key] = value
	return good_kwargs

def playlist_items_insert(client, properties, **kwargs):
	# See full sample for function
	resource = build_resource(properties)
	print(resource)
	# See full sample for function
	kwargs = remove_empty_kwargs(**kwargs)
	response = client.playlistItems().insert(body=resource,**kwargs).execute()
	#return print_response(response)
	return response

def add_playlist(youtube, pl_title, pl_description):
	body = dict( snippet=dict( title=pl_title, description=pl_description ), status=dict( privacyStatus='public' ) ) 
	playlists_insert_response = youtube.playlists().insert( part='snippet,status', body=body ).execute()
	print('New playlist ID: %s' % playlists_insert_response['id'])
	return playlists_insert_response

def create_playlist(client, pl_title,pl_description):
	#youtube = get_authenticated_service()
	try:
		return add_playlist(client, pl_title,pl_description)
	except HttpError as e:
		print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
		exit(e.resp.status)

def insert_videos(client, playlists_insert_response,video_id):
	pl_id = playlists_insert_response['id']
	#youtube = get_authenticated_service()
	if isinstance(video_id,str) and len(video_id) > 0:
		responses = playlist_items_insert( \
											client, { \
														'snippet.playlistId': pl_id\
														, 'snippet.resourceId.kind': 'youtube#video' \
														, 'snippet.resourceId.videoId': video_id \
													} \
											, part='snippet' \
										)
		return responses
	else:
		return None

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

def api_post(host_string, r_json):
	api_call_headers = {"Content-Type": "application/json"}
	r = requests.post( host_string , json = r_json , headers = api_call_headers)
	return True


# --------------------------------------------------
# server logic
# --------------------------------------------------

@app.route('/welcome',methods=['GET'])
def home():
	if 'credentials' not in session or 'session_id' not in session: return redirect('authorize')
	video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
	return render_template('/videos_added.html'\
									, intersex=video_ids \
									, latest_count=len(video_ids) \
									, total_count=session['numb_videos'] \
							)


@app.route('/query_builder',methods=['GET','POST'])
#@login_required
#@subscription_required
def query_builder():
	
	if 'credentials' not in session or 'session_id' not in session: return redirect('authorize')
	
	if request.method == 'GET':
		uniq_params = { tag : api_get_requests(API_URLS['unique_metadata'], {'tag':tag} ) for tag in TAGS }
		return render_template('/query-form.html' \
										, years=uniq_params['year'] \
										, genres=uniq_params['genre'] \
										, styles=uniq_params['style'] \
								)
	
	elif request.method == 'POST':
		print('POST',request)
		
		# ---- Query parameters
		
		wide_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in TAGS}
		artist_name = request.form.get('search:artist_name', type=str, default='')
		release_name = request.form.get('search:release_name', type=str, default='')
		label_name = request.form.get('search:label_name', type=str, default='')
		
		flash('Got your query...','message')
		
		# ---- Get master IDs from APIs
		
		artist_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'artist','name':artist_name} )
		release_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'release','name':release_name} )
		#label_ids = api_get_requests(API_URLS['ids_from_name'], {'name_type':'label','name':release_name} )
		master_ids_dict = api_get_requests(API_URLS['ids_from_metadata'], wide_query_dict )
		
		flash('Got the master release IDs...','message')
		
		# ---- Calculate Query (TODO move off to a seperate API ?)
		
		wide_query_sets = list_of_sets(master_ids_dict.values())
		
		if len(wide_query_sets) == 0:
			to_intersect = [artist_ids,release_ids]
		else:
			to_intersect = [artist_ids,release_ids,set.intersection(*wide_query_sets)]
		
		master_ids = list(set.intersection( *list_of_sets(to_intersect) ))
		
		flash('Aggregated the master release IDs...','message')
		
		if len(master_ids) == 0: return render_template('/no-results.html')
		
		# ---- Get video urls
		
		all_links = api_get_requests(API_URLS['video_urls'], {'master_ids': master_ids} )
		numb_links = len(all_links)
		
		flash('Got '+str(numb_links)+' video links...','message')
		
		if numb_links > 400:
			flash('Too many videos in query... There were '+str(numb_links)+'. Limit is 400.','message')
			return redirect('query_builder')
		
		if numb_links == 0: return render_template('/no-results.html')
		
		if 'numb_videos' not in session.keys(): session['numb_videos'] = numb_links
		else: session['numb_videos'] += numb_links
		
		# ---- Add to redis cache
		
		redis_query_cache_adds = api_put_requests( \
													API_URLS['video_query_cache'] \
													, { 'session_id' : session['session_id'] , 'video_ids': all_links } \
												)
		
		flash('Query results saved...','message')
		
		return render_template('/videos_added.html'\
										, intersex=all_links \
										, latest_count=numb_links \
										, total_count=session['numb_videos'] \
								)

@app.route('/current_urls',methods=["GET"])
def current_vids():
	if 'credentials' not in session or 'session_id' not in session: return redirect('authorize')
	
	video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
	
	return render_template('/videos_added.html'\
									, intersex=video_ids \
									, latest_count=len(video_ids) \
									, total_count=session['numb_videos'] \
							)

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
									
	return redirect(url_for('query_builder'))

@app.route('/create_playlist',methods=['GET','POST'])
def send_to_yt():
	
	if 'credentials' not in session or 'session_id' not in session: return redirect('authorize')
	
	if request.method == 'GET':
		video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
		return render_template('/playlist_details.html' \
										, numb_videos = len(video_ids)\
								)
		
	if request.method == 'POST':
		
		flash('Building youtube playlist...','message')
		
		title, desc = request.form.get('playlist_title'), request.form.get('playlist_desc')+'\n\nGenereated with the discogs-yt-playlister'
		
		# https://developers.google.com/youtube/v3/quickstart/python#further_reading
		
		# ---- Load the credentials from the session.
		
		credentials = google.oauth2.credentials.Credentials(**session['credentials'])
		client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
		
		video_ids = api_get_requests(API_URLS['video_query_cache'], {'session_id' : session['session_id']} )
		video_ids = [ video_id.lstrip('https://www.youtube.com/watch?v=') for video_id in video_ids]
		
		flash('Got your videos...','message')
		
		# ---- create a playlist
		
		playlist_result = create_playlist(client, title, desc)
		
		flash('Created playlist...','message')
		
		# ---- add the videos
		# - TODO move off to a seperate API (big queries results page times out)
		
		video_result = [ insert_videos(client, playlist_result , video_id ) for video_id in video_ids ]
		
		flash('Sent off videos...','message')
		
		#clear_cache = api_get_requests(API_URLS['video_query_cache_clear'], {'session_id' : session['session_id']} )
		#session.clear()
		
		# wait 5 seconds so youtube updates...
		
		time.sleep(2)
		
		return redirect( url_for('playlist_added/' \
										, playlist_title=str(title) \
										, playlist_id=str(playlist_result['id']) \
										, first_video=str(video_ids[0]) \
								))


@app.route('/playlist_added',methods=['GET'])
def playlist_added(playlist_title,playlist_id,first_video):
	return render_template('/playlist_added.html' \
									, pl_title=playlist_title\
									, pl_link=playlist_id\
									, first_vid=first_video \
							)
	
if __name__ == '__main__':
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	app.run(host='0.0.0.0',debug=True,port=80)
	#app.run(host='0.0.0.0',debug=False,port=80)