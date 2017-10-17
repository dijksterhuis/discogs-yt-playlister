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
	db.drop_collection(db_dict['coll'])
	c = db[db_dict['coll']]
	return c

def recursive_gen(in_json,tag,rec_counter):
	
	"""
	Looking for tags: @src, genre, style, year
	"""
	#for tag in tags:
	print(tag,rec_counter)
	print(in_json)
	print(in_json.keys())
	if rec_counter > 3:
		pass
	elif tag in in_json.keys():
		yield (tag, in_json['tag'])
	
	for item in in_json:
		print(item)
		rec_counter += 1
		recursive_gen(item,tag,rec_counter)
	
	for tag in ['genre','style','year','@src']:
		
	[( recursive_gen(master,'id',0) ), ( recursive_gen(master,'style',0) )]
	
	
	master_id = recursive_gen(master,'id',0)
	master_id = recursive_gen(master,'style',0)
	
	
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

	prints('script executing')
	starttime = dt.now()

	prints('Setting up Mongo connection')	

	db_dict = {'host' : 'discogs-mongo', 'port': 27017 , 'db' : 'discogs' , 'coll' : 'masters'}
	masters_coll = mongo_cli(db_dict)
	prints('Set up Mongo connection correctly (?)')
	for post in posts.find():	

	
	prints('Setting up Redis connections')

	r = redis.Redis(host='redis-metadata-master-ids',port='6379')
	
	if r.ping() is not True:
		print('Could not connect to the Redis Server, quitting')
		#os.EX_NOHOST
		exit(68)

	prints('Redis server pinged successfully!')
	
	prints('Opening masters file')
	#with open(args.masters_file[0],'r') as infile:
	#	masters = json.load(infile)['masters']['master']

	
	prints('Parsing through file with generator function')
	metadata_tags = ['genre','style','year','video']

	for tag,key,value in multi_tier_generator(masters,metadata_tags):
		prints(str(tag) + ' ' + str(key) + ' ' + str(value))
		r_io = r.sadd(tag + ':' + key, value)
		if r_io != 1:
			print('VALUES NOT ADDED: ' + str(tag) + ' ' + str(key) + ' ' + str(value))

	prints('Parsing complete!')
	elapsed_time = starttime - dt.now()
	print('time taken: ',elapsed_time.total_seconds())
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get master release IDs per genre then add to Redis")
	parser.add_argument('masters_file',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)