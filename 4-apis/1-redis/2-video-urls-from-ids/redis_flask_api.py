#!flask

#### EXTERNAL LIBRARY IMPORTS:

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from webargs.flaskparser import use_args

#### CUSTOM BUILD FUNCTION IMPORTS:

from api_build_funx import timer, make_json_resp, redis_host, get_videos, VIDEO_ARGS

"""
https://flask-restful.readthedocs.io/en/0.3.5/index.html
https://webargs.readthedocs.io/en/latest/index.html
"""

#### APP DEFs:

app = Flask(__name__)
auth = HTTPBasicAuth()

#### ENDPOINT DEFs:

@app.route('/', methods=['GET'])
def alive(self):
	return make_json_resp( {'status': 'OK'} )

@app.route('/video_urls', methods=['GET'])
@use_args(VIDEO_ARGS,locations=('json', 'form'))
def video_urls(args):
	req_time = timer()
	print(args)
	result = get_videos( args['master_ids'] )
	print('request time taken', req_time.time_taken() )
	return result

if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=5000,debug=True)
	app.run(host='0.0.0.0',port=80,debug=False)