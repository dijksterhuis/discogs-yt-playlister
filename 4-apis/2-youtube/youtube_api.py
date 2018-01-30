#!/usr/bin/env flask

""" Youtube RESTful API with flask """

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args
from webargs import fields


#### Youtube gen imports:

import googleapiclient.discovery
from googleapiclient.errors import HttpError
import google.oauth2.credentials
from youtube_playlist_gen import create_playlist, insert_videos

#### Google API DEFs:

CLIENT_SECRETS_FILE = "/home/client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

#### APP DEFs:

APP = Flask(__name__)
AUTH = HTTPBasicAuth()

#### API WEBARG DEFs:

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

def make_json_resp(in_data, resp):
    """ Turn in_data into a json response output """
    return make_response(jsonify(in_data), resp)

#### ENDPOINT DEFs:

@APP.route('/', methods=['GET'])
def alive():
    """ Is the API up and running check """
    return make_json_resp({'status': 'OK'}, 200)

@APP.route('/create_playlist', methods=['POST'])
@use_args(PLAYLIST_ARGS, locations=('json'))
def playlist_api(args):
    """ Create a new playlist using the given metadata and credentials
        Given a playlist metadata and user oauth credentials """
    credentials = google.oauth2.credentials.Credentials(**args['credentials'])
    client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    playlist_result = create_playlist(client, args['title'], args['desc'])
    return make_json_resp(playlist_result, 200)

@APP.route('/insert_videos', methods=['POST'])
@use_args(VIDEO_ARGS, locations=('json')
def video_insert_api(args):
    """ Insert videos into a specified playlist id
        Given a list of video ids and user oauth credentials """
    credentials = google.oauth2.credentials.Credentials(**args['credentials'])
    client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    for idx, video_id in enumerate(args['video_ids']):
        try:
            insert_videos(client, args['playlist_id'], video_id)
        except HttpError:
            print(idx, video_id, 'ERROR')


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000,debug=True)
    APP.run(host='0.0.0.0', port=80, debug=False)
