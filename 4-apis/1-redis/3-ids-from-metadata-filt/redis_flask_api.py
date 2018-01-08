#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, get_metadata_ids, make_json_resp,  METADATA_ID_ARGS

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
@use_args(METADATA_ID_ARGS,locations=('json', 'form'))
def metadata_ids(args):
	req_time = timer()
	print(args)
	#result = get_metadata_ids( args['metadata_filter_dict'] )
	print('request time taken', req_time.time_taken() )
	return make_json_resp( args['metadata_filter_dict'] , 200 )

if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=80,debug=True)
	app.run(host='0.0.0.0',port=80,debug=True)