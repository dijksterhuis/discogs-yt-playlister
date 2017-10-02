#!/usr/local/bin/python
import json, argparse, redis, os, pymongo
from joblib import Parallel,delayed
from sys import stdout as console
from sys import exit
from datetime import datetime as dt
"""
os import used for error codes on exits - could be useful for handling data problems at docker run time
see here: https://docs.python.org/2/library/os.html#process-management


TODO:

- PARAMETERIZE THIS?
- What code can be refactored?
	- What about otehr data files?
	- What can be reused from here for those files?
	- GENERATORS...?!?!
- Get artist names and ids?
- Get video TITLES:
	- Need to change the generator logic then...
	- Introduce a list of objects generator?
	- Will be needed for artists stuff too...
- Data quality > Accepted? - Year 0 problem
- This month's updates:
	- For 'new releases' filter
	- Only see stuff from the last month data dump
	- More redis instances... *sigh*
	- Add to main db, if added
- Changes to masters:
	- Data CAN change
	- Especially with newer releases
	- How to ensure proper update of sets?
	- Popping of old meta:tag index values?
	- Or copy entire db, reload entre thing, then redirect to updated version, flush old?
- Discogs links:
	- Add ALL links to discogs pages in youtube playlist description?
	- How about creating user lists alongside the playlists?

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
	
def redis_connections_check(conn_dict,connections):
	
	"""
	redis_conn_dict = ( \
			{'host':'redis-metadata-master-ids','port':6379} \
			, {'host':'redis-metadata-unique','port':6380} \
			, {'host':'redis-videos-masters','port':6381} \
			)
	"""
	
	connections_check = [connection.ping() for connection in connections]
	
	if False in connections_check:
		print('Could not connect to one of the Redis dbs, quitting')
		for idx,conn_str in enumerate(conn_dict):
			print( 'Server ' + str(idx+1) + ' of ' + str(len(conn_dict)) \
					+ ' host: ' + conn_dict['host'] + ' port: ' + conn_dict['port'] \
					+ ' connected: ' + connections_check[idx] \
					)
		#os.EX_NOHOST
		exit()
	else:
		prints('Redis servers pinged successfully!')
		return True
	
def main(args):
	
	"""
	1. Open a redis connection
	2. Open connection to masters collection
	3. Parse through the collection getting required bits
	4. Add the required lists to redis
	
	TODO
	- see above... plus:
	- How to handle data that only needs to be updated?
	- Change redis server connection string
	- secure redis?!
	"""

	starttime = dt.now()

	# ------------------------------------------

	prints('Setting up Mongo connection')
	
	# ---- Set up mongo db connection
	# is there a way to make this more dynamic?
	# argparse inputs?
	
	mongo_conn_dict = {'host' : 'mongo-discogs', 'port': 27017 , 'db' : 'discogs' , 'coll' : 'masters'}
	masters_coll = mongo_cli( mongo_conn_dict )
	prints('Connected to Mongo & /discogs/masters collection created!')
	
	prints('Setting up Redis connections')
	
	# ---- Set up the redis db connections
	# now using container networking, so port mappings not required
	# networking provides different ips, rather than ports

	redis_conn_dict = ( \
			{'host':'redis-metadata-master-ids','port':6379} \
			, {'host':'redis-metadata-unique','port':6379} \
			, {'host':'redis-videos-masters','port':6379} \
			)
			
	r_attrs_id, r_unique_attrs, r_videos = [redis.Redis( host=conn['host'], port=conn['port'] ) for conn in redis_conn_dict]
	
	redis_connections_check(redis_conn_dict,[r_attrs_id, r_unique_attrs, r_videos])

	# ------------------------------------------
	
	prints('Running through masters documents...')
	
	# ---- variable set up
	
	metadata_tags = ['genre','style','year','id','@src']
	masters = masters_coll.find()
	r_attrs_added , r_attrs_ignored , new_attrs, r_videos_added, r_videos_ignored = [0]*5
	
	prints('There are currently '+ str(masters_coll.count()) +' documents in the '+mongo_conn_dict['coll']+' collection')
	
	# ---- wait until there are enough records (100k minimum)
	# redis might overtake the mongo inserts otherwise
	
	waiter(masters_coll)
	
	# ------------------------------------------
	
	# ---- iterate through documents in mongo collection
	
	for idx, master in enumerate(masters):
		
		metadata_results_dict = { i : [] for i in metadata_tags}
		
		# ---- recurse through each document, find the required tags
		
		for tag in metadata_tags:
			for value in recursive_gen(master,tag,0):
				metadata_results_dict[tag].append(value)
		
		# ---- seperate out the id and video links
		# TODO - want video titles too ('title')??!?
		# BUT... 'title' of release is also 'title'
				
		discogs_id, videos = metadata_results_dict.pop('id')[0], metadata_results_dict.pop('@src')
		
		# ------------------------------------------
		
		# ---- pipeline redis set adds
		# WAY more efficient!
		# TODO but does it work with different instances?
		
		redis_attr_ops, redis_video_ops, pipe = list(),list(), r_attrs_id.pipeline()
		
		for key,item in redis_add_attributes_gen(metadata_results_dict):
			redis_attr_ops.append( r_attrs_id.sadd( key+':'+item,discogs_id ) )
			new_attrs += r_unique_attrs.sadd('unique:'+key,item)
			
		redis_video_ops = [r_videos.sadd('videos:'+discogs_id,video) for video in videos]
		
		pipe.execute()
		
		# ------------------------------------------
		
		# ---- update master_id counters for added to redis (or not)
		
		r_attrs_added += redis_attr_ops.count(1)
		r_attrs_ignored += redis_attr_ops.count(0)
		r_videos_added += redis_video_ops.count(1)
		r_videos_ignored += redis_video_ops.count(0)
		
		# ---- print information to stdout
		
		console.write( \
			'\r++ {} of {} -- attrs {} add, {} ign -- vid {} add, {} ign -- {} new attrs ++'.format( \
			idx+1, masters_coll.count(), r_attrs_added, r_attrs_ignored, r_videos_added, r_videos_ignored, new_attrs ))
		console.flush()
	
	# ------------------------------------------
		
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