#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, make_json_resp, redis_host, get_smembers, NAME_ARGS, IN_DATA_LOCS

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

@app.route('/get_ids_from_name', methods=['GET'])
@use_args(NAME_ARGS,locations=IN_DATA_LOCS)
def get_ids(args):
	req_time = timer()
	print(args)
	
	if args['name_type'] == 'artist_name':
		result = get_smembers('redis-artists-ids', args['name'])
		
	elif args['name_type'] == 'release_title':
		result = get_smembers('redis-masters-ids', args['name'])
		
	elif args['name_type'] == 'label_name': 
		result = get_smembers('redis-labels-ids', args['name'])
		
	print('request time taken', req_time.time_taken() )
	return result

if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=5000,debug=True)
	app.run(host='0.0.0.0',port=80,debug=False)