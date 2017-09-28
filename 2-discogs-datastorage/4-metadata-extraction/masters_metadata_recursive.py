#!/usr/local/bin/python
import json, argparse, redis, os, pymongo
from joblib import Parallel,delayed
from sys import stdout as console
from sys import exit
from datetime import datetime as dt
"""
os import used for error codes on exits - could be useful for handling data problems at docker run time
see here: https://docs.python.org/2/library/os.html#process-management
"""

def prints(string):
	if verbose_bool is True:
		print(string)

def io_err(e):
	print("Error: can't find file or read data")
	print(e)
	#os.EX_NOINPUT
	exit(66)

def mem_err(e):
	print("Memory Error!")
	print(e)
	exit()

def ass_err(e):
	print('File has a length <= 0')
	print(e)
	exit()

def key_err(e):
	print("There was a key error...")
	print(e)
	exit()

def index_err(e):
	print("There was a indexing error...")
	print(e)
	exit()

def unknown_err(e):
	print("An un-classified (non-captured exception) was raised, check traceback!")
	print(e)
	exit()

def multi_tier_generator(masters_file,tags):
	
	"""
	DEPRECIATED!
	
	Description + Pseudocode to go here...
	TODO
	Change log file paths (currently for local dev work)
	Description + Pseudocode
	"""
	
	with open('/logging/processed_ids.txt','a') as std_logs:
		with open('/logging/novalues_logfile.txt','a') as novalue_logs:
			#assert (total > 0),"File shouldn't have length 0"
			#total = len(masters_file)
			
			for idx, master_obj in enumerate(masters_file):
				for tag in tags:
					
					logs_string = 'file_idx|'+str(idx)+'|search_term|' + str(tag) + '|masterid|' + str(key) +'\n' 
					
					# ---- first tier
					if tag in master_obj.keys():
						yield ( tag , master_obj[ tag ] , master_obj["@id"] )
					
					# ---- second/third tier objects (nested)
					elif tag + 's' in master_obj.keys():
						for nested_obj in list(master_obj[ tag + 's' ].values() ):

							# ---- third tier objects (nested) - videos usually							
							if tag == 'video':
								for video_idx, video in enumerate(nested_obj):
									yield ( tag , master_obj["@id"] , video['@src'] )

							# ---- second/tier objects (nested)						
							else:
								yield ( tag , nested_obj , master_obj["@id"] )
					
					# ---- missing values & general process logging
					else:
						novalue_logs.write(logs_string)
						pass
					
					std_logs.write(logs_string)
					
					# ---- print process status info
					if verbose_bool is True:
						console.write("\r{} of {} -- ".format(idx+1, total))
						console.flush()
		
def mongo_cli(db_dict):
	m = pymongo.MongoClient(db_dict['host'],db_dict['port'])
	db = m[db_dict['db']]
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
	
	#if rec_counter > 200:
	#	pass
	
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

def waiter(masters_coll,mins_to_wait=10):
	waiting_counter = 0
	while masters_coll.count() < 100000:
		if waiting_counter > mins_to_wait:
			prints("Been waiting for 10 minutes, exiting with an error code")
			exit(404)
		prints('Need to wait for more data in mongo db... Waiting for 60 seconds')
		time.sleep(60)
	
def main(args):
	
	"""
	1. Open a redis connection
	2. Open the masters file
	3. Parse through the file getting required bits
	4. Add the required lists to redis
	
	TODO
	1 - Change filepaths - jsons + loggin
	2 - How to handle data that only needs to be updated?
	3 - Change redis server connection string
	4 - secure redis?!
	"""

	prints('Script executing')
	starttime = dt.now()

	prints('Setting up Mongo connection')
	
	# ---- Set up mongo db connection
	# is there a way to make this more dynamic?
	# argparse inputs?
	
	db_dict = {'host' : 'discogs-mongo', 'port': 27017 , 'db' : 'discogs' , 'coll' : 'masters'}
	masters_coll = mongo_cli(db_dict)
	prints('Mongo collection created')
	
	prints('Setting up Redis connections')
	
	# ---- Set up the redis db connections
	# TODO! This should really use the database pooling method
	# is there a way to make this more dynamic?
	# argparse inputs?
	
	r = redis.Redis(host='redis-metadata-master-ids',port='6379')
	r_buff = redis.Redis(host='redis-buffer-metadata-unique',port='6379')
	if r.ping() is not True or r_buff.ping() is not True:
		print('Could not connect to one of the Redis dbs, quitting')
		#os.EX_NOHOST
		exit(404)
		
	prints('Redis servers pinged successfully!')
	
	prints('Running through generator function')
	
	# ---- variable set up
	
	metadata_tags = ['genre','style','year','id','@src']
	masters = masters_coll.find()
	r_added , r_ignored , new_attrs = [0]*3
	
	prints('There are currently '+ str(masters_coll.count()) +' documents in the '+db_dict['coll']+' collection')
	
	# ---- wait until there are enough records (100k minimum)
	# redis might overtake the mongo inserts otherwise
	
	waiter(masters_coll)
	
	# ---- iterate through documents in mongo collection
	
	for idx, master in enumerate(masters):
		
		metadata_results_dict = { i : [] for i in metadata_tags}
		
		# ---- recurse through each document, find the required tags
		
		for tag in metadata_tags:
			for value in recursive_gen(master,tag,0):
				metadata_results_dict[tag].append(value)
		
		# ---- seperate out the id and video links
		# TODO - want video titles too??!?
				
		discogs_id = metadata_results_dict.pop('id')[0]
		videos = metadata_results_dict.pop('@src') # TODO !!
		
		# ---- pipeline redis set adds
		# WAY more efficient!
		
		redis_ops, pipe = list(), r.pipeline()
		
		for key,item in redis_add_attributes_gen(metadata_results_dict):
			redis_ops.append( r.sadd( key+':'+item,discogs_id ) )
			new_attrs += r_buff.sadd('unique:'+key,item)

		pipe.execute()

		# ---- collect some garbage
		# TODO should I bother?
		
		#del metadata_results_dict
		
		# ---- update master_id counters for added to redis (or not)
		
		r_added += redis_ops.count(1)
		r_ignored += redis_ops.count(0)
		
		# ---- print information to stdout
		
		console.write( \
			'\r++ {} processed of {} records -- {} added, {} ignore ++'.format( \
			idx,masters_coll.count(),r_added,r_ignored \
			))
		console.flush()
		
	prints('\nParsing complete!')
	elapsed_time = dt.now() - starttime
	prints('time taken (mins): '+str(elapsed_time.total_seconds()//60))
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get master release IDs per genre then add to Redis")
	parser.add_argument('masters_file',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)