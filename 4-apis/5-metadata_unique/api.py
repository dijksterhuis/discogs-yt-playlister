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

class get_metadata(Resource):
	def get(self):
		start_time = datetime.datetime.now()
		r = redis.Redis(host='redis-metadata-unique',port=6379)
		try:
			r.ping()
		except:
			return make_response('Database connectivity issues', 500)
		
		unique_params = { tag : [i.decode('utf-8') for i in list(r.smembers('unique:'+tag))] for tag in ['year','genre','style']}
		
		for key in unique_params:
			unique_params[key].sort()
		
		print('request start' , start_time ,'request duration: ' , time_delta.total_seconds())
		return make_response(unique_params, 200)
		
api.add_resource( am_i_alive , '/am_i_alive' )
api.add_resource( get_metadata , '/get_metadata')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)