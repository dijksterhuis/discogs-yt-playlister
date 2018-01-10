#!/usr/local/bin/python
import json, argparse, redis, os, pymongo, time
from sys import stdout as console
from sys import exit
from datetime import datetime as dt

"""
TODO - docstring... (need to test first...)
"""

def print_verbose(string):
	"""
	Print the string if verbosity (argparse arg) is true
	"""
	if verbose_bool is True:
		if type(string) is list: print(*string)
		else: print(string)

def recursive_gen(in_json,tag,rec_counter):
	
	"""
	Recursively look for and yield tags from Mongo documents
	@src, genre, style, year, artist_id etc.
	"""
	# -- we've gone down one level of nesting / recursion
	
	rec_counter += 1
	
	# -- we found the item(s) we're looking for!
	
	if type(in_json) is dict and tag in in_json.keys(): yield in_json[tag]
		
	# -- else then we're at the bottom of the json object, skip
	
	elif type(in_json) is str: pass
	
	# if list, we need to iterate over the list elements and redo recursion
	
	elif type(in_json) is list:
		for list_item in in_json:
			for value in recursive_gen(list_item,tag,rec_counter): yield value
	
	# -- no found key, another level we can go to
	
	elif type(in_json) is dict:
		for key in in_json:
			for value in recursive_gen(in_json[key],tag,rec_counter): yield value
				
	# ---- nothing found, ignore
	
	else: pass

def get_values(metadata_tags,document):
	
	for tag in metadata_tags:
		val = [value for value in recursive_gen(document,tag,0)]
		if len(val) > 1: yield (tag, val)
		elif len(val) == 0: yield (tag, None)
		else: yield (tag,val[0])

def mongo_connect(mongo_conn_host):
	
	"""
	Connect to Mongo instance
	"""
	
	print_verbose( ['Setting up Mongo DB connection to: ', mongo_conn_host] )
	mongo_conn_dict = { 'host' : 'mongo-discogs-' + mongo_conn_host, 'port' : 27017, 'db' : 'discogs', 'coll' : mongo_conn_host }
	
	m = pymongo.MongoClient(mongo_conn_dict['host'],mongo_conn_dict['port'])
	db = m[mongo_conn_dict['db']]
	print_verbose(['Mongo connection ping result: ',db.command('ping')])
	c = db[mongo_conn_dict['coll']]
	
	return c

def redis_connect(redis_conn_host):
	
	"""
	Connect to Redis instance
	"""
	
	print_verbose( ['Setting up Redis Connection to: ', redis_conn_host] )
	redis_conn = redis.Redis( host=redis_conn_host, port=6379 )
	outputs = [ redis_conn ]
	
	ping_result = redis_conn.ping()
	print_verbose( ['Redis connection ping result: ',ping_result ] )
	
	if ping_result is False:
		print('COULD NOT CONNECT TO '+redis_conn_host+'. EXITING.')
		exit(500)
	
	init_redis_dbsize = redis_conn.dbsize()
	
	if init_redis_dbsize == 0:
		print('NO DATA IN '+redis_conn_host+'. EXITING.')
		exit(0)
		
	print('Currently '+str(init_redis_dbsize)+' keys in '+redis_conn_host)
	
	print_verbose('Setting up Redis Pipeline.')
	
	return redis_conn, redis_conn.pipeline(), init_redis_dbsize

def redis_inserts(redis_conn, key, value, list_check = None ):
	
	""" 
	Simple set insert logic for Redis
	------------------------------------------------
	- Videos come in a list, so VALUE must be iterated over. (master_id : video_urls )
	- Genres come in a list, so KEY must be iterated over. (genre : master_id)
	"""
	
	if list_check == 'key' and isinstance(key, list):
		adds = sum([ redis_conn.sadd( str(key_item), str(value) ) for key_item in key ])
		
	elif list_check == 'value' and isinstance(value, list):
		adds = sum([ redis_conn.sadd( str(key) , str(list_item) ) for list_item in value ])
		
	else:
		adds = redis_conn.sadd( str(key), str(value) )
		
	return adds

def main(args):
	
	"""
	1. Open a redis connection
	2. Open a mongo connection
	3. Iterate over mongo dox
	4. Get the required bits from mongo
	5. Insert into redis
	5. Stats print out
	"""
	
	run_type, redis_conn_host, mongo_conn_host, r_key, r_value = \
		 	args.run_type[0], args.redis_insert_host[0], args.mongo_connection_host[0], args.redis_key[0], args.redis_value[0]
	
	print('\nSetting up database connections.')
	
	redis_conn, r_pipeline, init_redis_dbsize = redis_connect(redis_conn_host)
	mongo_conn = mongo_connect(mongo_conn_host)
	
	print('DB connections set up, beginning data extraction...\n')
	
	dataset, starttime, counter = mongo_conn.find(), dt.now(), 0
	
	for idx, document in enumerate( dataset ):
		
		metadata_tags = [ r_key, r_value ]
		inserts = { key: value for key, value in get_values( metadata_tags,document ) }
		
		# ---- add to redis
		
		if inserts[r_value] == None or inserts[r_key] == None:
			
			print('Missing key and/or value:')
			print(r_key, inserts[r_key])
			print(r_value, inserts[r_value])
			print('\n')
			
		elif run_type == 'simple_set':
			
			# ---- Simple set inserts e.g. release_title : masters_id
			counter += redis_inserts(redis_conn, inserts[r_key], inserts[r_value], list_check = 'value' )
			
		elif run_type == 'meta_uniq_set':
			
			# ---- Metadata inserts e.g. genre (list) : masters_id
			# - N.B. inserts[r_key] is passed here instead of inserts
			counter += redis_inserts(redis_conn, inserts[r_key], inserts[r_value], list_check = 'key' )
			
		elif run_type == 'autocomplete':
			
			# ---- autocomplete redis logic e.g. artist-name : ( Holden , 5 )
			# - TODO - this needs work... bigger issues to get on with...
			# - ZSCORE returns None if members doesn't exist in set
			# - Set initial score to 1, increment for each additional occurance
			# - This will rank release titles (for example) by number of occurances
			# - More common names then turn up higher in the autocomplete searches
			
			if redis_conn.zscore( r_value, inserts[r_value] ) == None:
				counter += redis_conn.zadd( r_value, inserts[r_value], 0)
			else:
				redis_conn.zincrby( r_value, inserts[r_value], amount = 1)
				
		# ---- stats
		
		console.write( "\r{:,d} proc / {:,d} mongo dox".format( idx, mongo_conn.count() ))
		console.flush()
	
	# ---- execute redis pipeline
	
	print_verbose('Executing redis pipeline.')
	r_pipeline.execute()
	
	# ---- print stats
	
	elapsed_time, redis_additions = dt.now() - starttime, redis_conn.dbsize() - init_redis_dbsize
	print('\nExtraction complete!')
	print_verbose( '{:,d} keys were actually added to the {:s} Redis DB'.format(redis_additions, redis_conn_host) )
	print_verbose( 'Redis counter is at: {:,d}. Does this match?'.format(counter) )
	print_verbose('Time taken (mins): {:,d}'.format(elapsed_time.total_seconds()//60) )

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description="REDIS *SET* INSERTS: Get data from Mongo and load into Redis")
	
	parser.add_argument('run_type',type=str,nargs=1,choices=['simple_set','meta_uniq_set','autocomplete'])
	parser.add_argument('mongo_connection_host',type=str,nargs=1,choices=['masters','labels','releases','artists'])
	parser.add_argument('redis_insert_host',type=str,nargs=1)
	parser.add_argument('redis_key',type=str,nargs=1)
	parser.add_argument('redis_value',type=str,nargs=1)
	parser.add_argument('--verbose','-v',action='store_true')
	
	args = parser.parse_args()
	
	global verbose_bool
	verbose_bool = args.verbose
	
	main(args)