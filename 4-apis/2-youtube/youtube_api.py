#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args


#### Youtube gen imports:
import googleapiclient.discovery
import google_auth_oauthlib.flow
import google.oauth2.credentials
from youtube_playlist_gen import create_playlist, insert_videos

#### Google API VAR DEFs:

CLIENT_SECRETS_FILE = "/home/client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

#### APP DEFs:

app = Flask(__name__)
auth = HTTPBasicAuth()

#### API ARG DEFs:

PLAYLIST_ARGS = { \
					'credentials': fields.Dict(required=True) \
					, 'title' : fields.Str(required=True) \
					, 'description': fields.Str(required=True) \
				}

VIDEO_ARGS = { \
				'credentials': fields.Dict(required=True) \
				, 'playlist_id' : fields.Str(required=True) \
				, 'video_ids': fields.List(fields.Str(required=True)) \
			}

#### FUNCTION DEFs:

def make_json_resp(in_data,resp):
	return make_response( jsonify( in_data ), resp )

#### ENDPOINT DEFs:

@app.route('/', methods=['GET'])
def alive():
	return make_json_resp( {'status': 'OK'} , 200 )

@app.route('/create_playlist', methods=['POST'])
@use_args(PLAYLIST_ARGS,locations=('json', 'form'))
def create_playlist(args):
	credentials = google.oauth2.credentials.Credentials(**args['credentials'])
	client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
	playlist_result = create_playlist(client, args['title'], args['desc'])
	return make_json_resp( playlist_result, 200 )

@app.route('/insert_videos', methods=['POST'])
@use_args(VIDEO_ARGS,locations=('json', 'form'))
def create_playlist(args):
	credentials = google.oauth2.credentials.Credentials(**args['credentials'])
	client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
	playlist_results = [ insert_videos(client, args['playlist_id'],video_id) for video_id in args['video_id'] ]
	

if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=5000,debug=True)
	app.run(host='0.0.0.0',port=80,debug=False)