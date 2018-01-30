#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, make_json_resp, AUTOCOMPLETE_ARGS

"""
https://flask-restful.readthedocs.io/en/0.3.5/index.html
https://webargs.readthedocs.io/en/latest/index.html
"""

#### APP DEFs:

app = Flask(__name__)
auth = HTTPBasicAuth()

#### ENDPOINT DEFs:

@app.route('/', methods=['GET'])
def alive():
    return make_json_resp( {'status': 'OK'} , 200 )

@app.route('/artist', methods=['GET'])
@use_args(AUTOCOMPLETE_ARGS,locations='json')
def artist(args):
    req_time = timer()
    if request.method == 'GET':
        result = get_video_ids_cache( 'artist', args['value'] )
    print('request time taken', req_time.time_taken() )
    return result

@app.route('/release', methods=['GET'])
@use_args(AUTOCOMPLETE_ARGS,locations='json')
def release(args):
    req_time = timer()
    if request.method == 'GET':
        result = get_video_ids_cache( 'release', args['value'] )
    print('request time taken', req_time.time_taken() )
    return result


@app.route('/label', methods=['GET'])
@use_args(AUTOCOMPLETE_ARGS,locations='json')
def label(args):
    req_time = timer()
    if request.method == 'GET':
        result = get_video_ids_cache( 'label', args['value'] )
    print('request time taken', req_time.time_taken() )
    return result


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(host='0.0.0.0',port=80,debug=False)