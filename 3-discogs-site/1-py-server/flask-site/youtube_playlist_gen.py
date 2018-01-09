# This code sample creates a private playlist in the authorizing user's
# YouTube channel.
# Usage:
# 	python playlist_updates.py --title=<TITLE> --description=<DESCRIPTION> --video_ids=<VIDEO_ID>

import argparse
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

CLIENT_SECRETS_FILE = '/home/client_secrets.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ['https://www.googleapis.com/auth/youtube']
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
														'snippet.playlistId': pl_id \
														, 'snippet.resourceId.kind': 'youtube#video' \
														, 'snippet.resourceId.videoId': video_id \
													} \
											, part='snippet' \
										)
		return responses
	else:
		return None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--title', type=str, nargs=1 \
										, default='Test Playlist'\
										, help='The title of the new playlist.')
	parser.add_argument('--description', type=str, nargs=1 \
										, default='A private playlist created with the YouTube Data API.' \
										, help='The description of the new playlist.')
	parser.add_argument('--video_ids', type=str, nargs='+', dest = 'video_ids' \
										,help='Video ID(s) to add to the playlist.')
	args = parser.parse_args()
	insert_videos( create_playlist(args.title,args.description), args.video_ids)