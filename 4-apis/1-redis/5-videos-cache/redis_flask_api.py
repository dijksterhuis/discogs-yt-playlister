#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, make_json_resp, get_video_ids_cache, put_video_ids_cache, clear_video_ids_cache, V_CACHE_ARGS, IN_DATA_LOCS, max_query_id

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

@app.route('/video_query_cache', methods=['GET','PUT'])
@use_args(V_CACHE_ARGS,locations=IN_DATA_LOCS)
def vid_cache_add(args):
    req_time = timer()
    print(args)
    if request.method == 'GET':
        result = get_video_ids_cache( args['session_id'] )
    elif request.method =='PUT':
        result = put_video_ids_cache( args['session_id'], args['video_ids'] )
    print('request time taken', req_time.time_taken() )
    return result

@app.route('/video_query_cache_clear', methods=['GET'])
@use_args(V_CACHE_ARGS,locations=IN_DATA_LOCS)
def vid_cache_clear(args):
    req_time = timer()
    print(args)
    result = clear_video_ids_cache(args['session_id'])
    print('request time taken', req_time.time_taken() )
    return result

@app.route('/max_query_id', methods=['GET'])
def get_new_id():
    result = max_query_id()
    return result

if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(host='0.0.0.0',port=80,debug=False)