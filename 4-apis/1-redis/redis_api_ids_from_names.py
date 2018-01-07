#!flask/bin/python
from flask import Flask, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from flask_restful import abort, Resource, Api, marshal_with, fields #, reqparse - depreciated
from webargs import fields
from webargs.flaskparser import use_args
import json, os, datetime, time, redis, werkzeug, requests, flask

"""
https://flask-restful.readthedocs.io/en/0.3.5/index.html
OLD VERSION - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""

#### APP DEFs:

app = Flask(__name__)
#api = Api(app)
auth = HTTPBasicAuth()

#resource_fields = {'name': fields.String, 'tag': fields.String,'date_updated': fields.DateTime(dt_format='rfc822')}

name_args = { 'name': fields.Str(required=True) }
tag_args = { 'tag': fields.Str(required=True) }
video_args = { 'master_ids': fields.List(fields.Str()) }
metadata_id_args = { 'year': fields.List(fields.Str()), 'style' : fields.List(fields.Str())  , 'genre' : fields.List(fields.Str()) }

#### EXECUTION DEFs:


class timer:
	def __init__(self):
		#import datetime
		self.start = datetime.datetime.now()
	def time_taken(self):
		c_time = datetime.datetime.now() - self.start
		return c_time.total_seconds()

def make_json_resp(in_data,resp):
	return make_response( jsonify( in_data ), resp )

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
	except:
		return ConnectionError

def get_smembers(host_string, value):
	print(value)
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

def get_unique_metadata( tag ):
	r = redis_meta_host(tag)
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	metadata = get_redis_keys(r).sort()
	return make_json_resp( metadata , 200)

#### RESOURCE DEFs:

@app.route('/', methods=['GET'])
def alive(self):
	return make_json_resp( {'status': 'OK'} )

@app.route('/artist_name_ids', methods=['GET'])
@use_args(name_args,locations=('querystring','json', 'form'))
def artist_name_ids(args):
	req_time = timer()
	print(args['name'])
	result = get_smembers('redis-artists-ids', args['name'])
	print('request time taken', req_time.time_taken() )
	return result
		
@app.route('/release_name_ids', methods=['GET'])
@use_args(name_args,locations=('querystring','json', 'form'))
def release_name_ids(args):
	req_time = timer()
	print(args['name'])
	result = get_smembers('redis-masters-ids', args['name'])
	print('request time taken', req_time.time_taken() )
	return result

@app.route('/label_name_ids', methods=['GET'])
@use_args(name_args,locations=('querystring','json', 'form'))
def label_name_ids(args):
	req_time = timer()
	print(args['name'])
	result = make_json_resp( {"ERROR": "Not implemented yet" } , 400 )
	#result = get_master_ids('redis-labels-ids', get_value)
	print('request time taken', req_time.time_taken() )
	return result

@app.route('/video_urls', methods=['GET'])
@use_args(video_args,locations=('json', 'form'))
def video_urls(args):
	req_time = timer()
	result = get_videos( args['master_ids'] )
	print('request time taken', req_time.time_taken() )
	return result
		
@app.route('/metadata_ids', methods=['GET'])
@use_args(metadata_id_args,locations=('json', 'form'))
def metadata_ids(args):
	req_time = timer()
	result = metadata_ids( args )
	print('request time taken', req_time.time_taken() )
	return result

@app.route('/unique_metadata', methods=['GET'])
@use_args(tag_args,locations=('querystring','json', 'form'))
def unique_metadata(args):
	req_time = timer()
	result = get_unique_metadata( args['tag'] )
	print('request time taken', req_time.time_taken() )
	return result


#### APP EXECUTE:

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)
	#app.run(host='0.0.0.0',port=80,debug=False)