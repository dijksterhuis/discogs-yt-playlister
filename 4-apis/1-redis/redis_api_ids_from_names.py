#!flask/bin/python
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, abort, Resource, Api, make_response
import json, os, datetime, time, redis, werkzeug, requests, flask

"""
https://flask-restful.readthedocs.io/en/0.3.5/index.html
OLD VERSION - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""

#### APP DEFs:

app, api, auth = Flask(__name__), Api(app), HTTPBasicAuth()

#### EXECUTION DEFs:

class timer:
	def __init__(self):
		#import datetime
		self.start = datetime.datetime.now()
	def time_taken(self):
		c_time = datetime.datetime.now() - self.start
		return c_time.total_seconds()

def make_json_resp(in_data):
	return make_response( jsonify( in_data ))

def redis_meta_host(value):
	return redis.Redis(host='redis-metadata-unique-'+value,port=6379)

def redis_host(value):
	return redis.Redis(host=value,port=6379)

def get_redis_values(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

def get_redis_keys(redis_instance):
	return [i.decode('utf-8') for i in list(redis_instance.keys())]

def redis_conn_check(redis_connection_pool):
	try:
		redis_connection_pool.ping()
		return True
	except redis.exceptions.ConnectionError as e:
		return e

def get_smembers(host_string, value):
	
	r = redis_host( host_string )
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
		
	result = get_redis_values( r , value)
	return make_json_resp( result , 200)

def put_smembers(host_string, key, value):
	
	r = redis_host( host_string )
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
		
	result = r.sadd(key, value)
	
	if result == 1:
		return make_json_resp( {put_key:'OK'} , 200)
	else:
		return make_json_resp( {put_key:'ERROR'} , 500)

def get_videos( master_ids_list ):
	
	all_links = list()
	
	r = redis_host( 'redis-video-id-urls' )
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	pipe = r.pipeline()
	
	for master_id in master_ids_list:
		if isinstance( master_id, bytes ): master_id = str( master_id.decode('utf-8') )
		links = get_redis_values( r, master_id )
		if len(links) == 0: pass
		elif len(links) == 1 and type(links) is list: all_links.append( links[0] )
		elif isinstance( links, list) :
			for link in links: all_links.append(link)
		else: pass
		
	pipe.execute()
	
	return make_json_resp(all_links , 200 )

def metadata_ids(query_dict):
	
	scards_dict, master_ids_dict = dict(), dict()
	
	# get master IDs for wide filters
	
	if len(query_dict) == 0:
		return make_response( "No data provided." , 400 )
	
	for key in query_dict.keys():
		if len(query_dict[key]) == 0: pass
		else:
			r = redis_meta_host(key)
			
			ping_check = redis_conn_check(r)
			if ping_check != True:
				return make_response( ping_check, 500 )
			
			p = r.pipeline()
			
			for value in query_dict[key]:
				scards_dict[key] = sum([ redis_meta_host(key).scard(value) for value in query_dict[key] ])
				master_ids_dict[key] = set.union(*[ redis_meta_host(key).smembers(value) for value in query_dict[key] ])
				
			p.execute()
			
	return make_json_resp(master_ids_dict , 200 )

def get_unique_metadata(tag):
	r = redis_meta_host(tag)
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	metadata = get_redis_keys(r).sort()
	return make_json_resp( metadata , 200)

#### RESOURCE DEFs:

class am_i_alive(Resource):
	def get(self):
		return make_json_resp( {'status': 'OK'} )

class artist_name_ids(Resource):
	def get(self, get_value):
		req_time = timer()
		result = get_smembers('redis-artists-ids', get_value)
		print('request time taken', req_time.time_taken() )
		return result
		
class release_name_ids(Resource):
	def get(self, get_value):
		req_time = timer()
		result = get_smembers('redis-masters-ids', get_value)
		print('request time taken', req_time.time_taken() )
		return result

class label_name_ids(Resource):
	def get(self, get_value):
		req_time = timer()
		result = make_json_resp( {"ERROR": "Not implemented yet" } , 400 )
		#result = get_master_ids('redis-labels-ids', get_value)
		print('request time taken', req_time.time_taken() )
		return result

class video_urls(Resource):
	def get(self, master_ids_list):
		req_time = timer()
		result = get_videos( master_ids_list )
		print('request time taken', req_time.time_taken() )
		return result
		
class get_metadata_ids(Resource):
	def post(self):
		req_time = timer()
		result = metadata_ids(request.data)
		print('request time taken', req_time.time_taken() )
		return result

class get_unique_metadata(Resource):
	def get(self,tag):
		req_time = timer()
		result = get_unique_metadata(tag)
		print('request time taken', req_time.time_taken() )
		return result

#### ENDPOINT DEFs:

api.add_resource( am_i_alive , '/am_i_alive' )
api.add_resource( artist_name_ids , '/artist_name_ids/<string:get_value>' )
api.add_resource( release_name_ids , '/release_name_ids/<string:get_value>' )
api.add_resource( label_name_ids , '/label_name_ids/<string:get_value>' )
api.add_resource( video_urls , '/video_urls/<int:master_id>' )
api.add_resource( get_metadata_ids , '/get_metadata_ids' )

#### APP EXECUTE:

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)
	#app.run(host='0.0.0.0',port=80,debug=False)