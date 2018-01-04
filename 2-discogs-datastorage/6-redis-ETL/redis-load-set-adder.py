#!/usr/local/bin/python
import json, argparse, redis, os, pymongo, time
from sys import stdout as console
from sys import exit
from datetime import datetime as dt

"""
TODO - docstring... (need to test first...)
"""

def mongo_cli(db_dict):
	m = pymongo.MongoClient(db_dict['host'],db_dict['port'])
	db = m[db_dict['db']]
	print_verbose('Mongo connection ping result: ',db.command('ping'))
	c = db[db_dict['coll']]
	return c

def recursive_gen(in_json,tag,rec_counter):
	
	"""
	Looking for tags: @src, genre, style, year
	"""
	
	#if type(in_json) is dict:
	#	print(0,tag,rec_counter,in_json.keys())
	#else:
	#	print(0,tag,rec_counter,in_json)
	
	rec_counter += 1
	
	# ---- we found the item(s) we're looking for!
	
	if type(in_json) is dict and tag in in_json.keys():
		#print(1,tag, in_json[tag],rec_counter)
		yield in_json[tag]

	# ---- if it's a string 
	# ---- then we're at the bottom of the json object
	
	elif type(in_json) is str:
		#print(2,in_json,rec_counter)
		pass
	
	# ---- if it's a list (probably videos) 
	# ---- we need to iterate over the list elements
	
	elif type(in_json) is list:
		#print(3,in_json,rec_counter)
		for list_item in in_json:
			#print('3a',list_item,rec_counter)
			for value in recursive_gen(list_item,tag,rec_counter):
				#print('3b',tag,value,rec_counter)
				yield value
	
	# ---- we haven't found the item(s) we're looking for
	# ---- but we've got another nested object to search through
	
	elif type(in_json) is dict:
		for key in in_json:
			for value in recursive_gen(in_json[key],tag,rec_counter):
				#print(4,tag,value,rec_counter)
				yield value

	# ---- else this is not useful data, ignore
	# ---- TODO what actually gets outputted here?
	
	else:
		#print(5,in_json)
		pass

def redis_add_attributes_gen(my_dict):
	
	"""
	Can have multiple styles
	But only one genre or year
	So need logic to handle that
	(genre/year NOT stored as lists)
	"""
	
	for key in my_dict:
		for dict_item in my_dict[key]:
			if type(dict_item) is list:
				for item in dict_item:
					yield key, item
			else:
				yield key, dict_item

def main(args):
	
	"""
	1. Open a redis connection
	2. Open connection to a mongo instance
	3. Open connection to a redis instance
	4. Get the required bits from mongo and insert into redis
	5. Stats print out
	"""
	
	starttime = dt.now()
	
	# ---- set up redis connection
	print_verbose('Setting up Redis Connection to: ',args.redis_connection_host)
	redis_conn = redis.Redis(host=args.redis_connection_host, port=6379)
	print_verbose('Redis connection ping result: 'redis_conn.ping())
	print_verbose('Setting up Redis Pipeline.')
	r_pipeline = redis_conn.pipeline()
	entries_added_to_redis = 0
	
	# ---- set up mongo connection
	print_verbose('Setting up Mongo DB connection to: ',args.mongo_connection_host)
	mongo_conn_dict = {'host':'mongo-discogs-'+args.mongo_connection_host,'port':27017,'db':'discogs','coll':args.mongo_connection_host}
	mongo_conn = mongo_cli( mongo_conn_dict )
	dataset = mongo_conn.find()
	
	# ---- get the required data from mongo collection
	for idx, document in enumerate(dataset):
		metadata_tags = [args.redis_key , args.redis_value ]
		
		# ---- tuples can be used in dictionary construction, handy for complex if/else statements
		# https://stackoverflow.com/a/43390527/5945794
		inserts = dict( \
							(tag : [value for value in recursive_gen(master,tag,0)] ) \
								if len([value for value in recursive_gen(master,tag,0)]) > 1 \
								else (tag : [value for value in recursive_gen(document,tag,0)][0]) \
								for tag in metadata_tags \
							)
		
		# ---- add to redis
		entries_added_to_redis += redis_conn.sadd( inserts['release_title'] , inserts['masters_id'] )
		
		# ---- stats
		console.write( "\r{} proc / {} mongo dox - to add to redis: {}".format(idx,mongo_conn.count(),entries_added_to_redis))
		console.flush()
	
	# ---- finish up
	
	print_verbose('Executing redis pipeline.')
	r_pipeline.exec()
	print('\nParsing complete!')
	elapsed_time = dt.now() - starttime
	print('time taken (mins): '+str(elapsed_time.total_seconds()//60))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="REDIS *SET* INSERTS: Get data from a Mongo collection and load into a Redis instance")
	parser.add_argument('mongo_connection_host',type=str,nargs=1,choices=['masters','labels','releases','artists'])
	parser.add_argument('redis_connection_host',type=str,nargs=1)
	parser.add_argument('redis_key',type=str,nargs=1)
	parser.add_argument('redis_value',type=str,nargs=1)
	parser.add_argument('--verbose','-v',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)