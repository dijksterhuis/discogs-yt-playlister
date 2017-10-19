#!flask/bin/python
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, abort, Resource, Api
import json, os, datetime, time, redis, werkzeug, requests, flask

"""
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

r_videos = redis.Redis('redis-videos-masters','6379')
r_cache = redis.Redis('redis-query-cache','6379')

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
        return {'status': 'OK'}

class video_urls(Resource):
	def post(self):
		
		start_time = datetime.datetime.now()
		print('request start',start_time)
		
		# - get request - be nice if reqparse could be used for this...
		
		query_dict = request.get_json()
		print('query: ',query_dict)
		
		video_urls = r_videos.smembers([ master_id for master_id in query_dict['video-ids'])
		
		# TODO
		session_query_id = '1111'
		
		r_cache.sadd( session_query_id , video_urls )
		
		print('results: ',results)
		print('numb results: ',len(results))
		
		time_delta = datetime.datetime.now() - start_time
		print('request duration: ',time_delta.total_seconds())
		
		# - return the cache set's id to be fed into the youtube api playlist generator
		
		return session_query_id, 201

api.add_resource(am_i_alive ,'/am_i_alive')
api.add_resource(masters, '/video_urls')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)
	#app.run(debug=True,port=80)