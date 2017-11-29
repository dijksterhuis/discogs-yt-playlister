#!flask/bin/python
from flask import Flask, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, abort, Resource, Api
import json, os, datetime, time, redis, werkzeug, requests, flask

"""
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class am_i_alive(Resource):
	def get(self):
		return make_response(jsonify({'status': 'OK'}),200)

class get_id(Resource):
	def get(self, master_id):
		start_time = datetime.datetime.now()
		r = redis.Redis('redis-video-id-urls','6379')
		try:
			r.ping()
		except:
			return make_response('Database connectivity issues', 500)
		video_urls = r.smembers( master_id )
		time_delta = datetime.datetime.now() - start_time
		print('request start' , start_time ,'request duration: ' , time_delta.total_seconds(), 'request', master_id, 'result', video_urls)
		if len(release_id) == 0:
			return make_response("No data", 400)
		else:
			return make_response(video_urls, 200)

api.add_resource( am_i_alive , '/am_i_alive' )
api.add_resource( get_id , '/get_id/<string:master_id>' )

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)