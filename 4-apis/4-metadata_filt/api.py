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

class search_releases(Resource):
	def get(self, string_value):
		return make_response('TODO', 200)

class get_id(Resource):
	def post(self):
		start_time = datetime.datetime.now()
		r = redis.Redis('redis-metadata-filtering','6379')
		try:
			r.ping()
		except:
			return make_response('Database connectivity issues', 500)
		release_id = r_masters.smembers( release_name )
		time_delta = datetime.datetime.now() - start_time
		print('request start' , start_time ,'request duration: ' , time_delta.total_seconds(), 'request', release_name, 'result', release_id)
		if len(release_id) == 0:
			return make_response("No data", 400)
		else:
			return make_response(release_id, 200)

api.add_resource( am_i_alive , '/am_i_alive' )
api.add_resource( get_id , '/get_id/<string:release_name>' )
api.add_resource( search_releases , '/search_releases/<string:string_value>' )

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)