#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, make_json_resp, get_metadata_ids, METADATA_ID_ARGS, IN_DATA_LOCS

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

@app.route('/ids_from_metadata', methods=['GET'])
@use_args(METADATA_ID_ARGS,locations=IN_DATA_LOCS)
def get_ids(args):
	req_time = timer()
	print(args)
	result = get_metadata_ids( args )
	print('request time taken', req_time.time_taken() )
	return result

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug=False)