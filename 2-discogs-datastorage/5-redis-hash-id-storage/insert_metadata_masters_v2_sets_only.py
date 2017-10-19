#!/usr/local/bin/python
import json, argparse, redis, os, pymongo, time
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

#### ------------------------------------------
#### Util functions
#### ------------------------------------------

def prints(string):
	if verbose_bool is True:
		print(string)

def waiter(masters_coll):
	"""
	Checks is mongo collection is being updated, if so enters a waiting period
	"""

	prints('Checking if mongo is being updated, give me 30 seconds...')

	count_1 = masters_coll.count()
	time.sleep(30)
	count_2 = masters_coll.count()

	if count_2 != count_1:
		prints('Seems that mongo is being updated, entering a waiting routine...')
		waiting_count = 0
		while (count_2 != count_1):
			if (waiting_counter % 5) == 0:
				prints('Mongo still updating. Waiting. Waited for ' + str(waiting_count) + ' minutes')
			count_1 = masters_coll.count()
			time.sleep(60)
			count_2 = masters_coll.count()
			waiting_count += 1
	else:
		prints('Seems that mongo is not being updated, continuing...')

def tuplize(*v):
	'''
	From variable v, return a one-element tuple (v,)
	For v = 1, return = (1,)
	'''
	return(v)

#### ------------------------------------------
#### Error functions (TODO)
#### ------------------------------------------

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

#### ------------------------------------------
#### Data Generators
#### - Process data through a specified iterable
#### ------------------------------------------

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

def hash_stats_gen(redis_hash_ops_results):
	for key, value in redis_hash_ops_results.items():
		if type(value) is list:
			for v in value:
				if v is True:
					yield (key, 'add')
				else:
					yield (key, 'ign')
		else:
			if value is True:
				yield (key, 'add')
			elif value is False:
				yield (key, 'ign')

def sets_stats_gen(redis_set_ops_results):
	for key in redis_set_ops_results.keys():
		for t in [('add',1), ('ign',0)]:
			if type(redis_set_ops_results[ key ]) is int \
			and redis_set_ops_results[ key ] in t:
				yield (key, t[0], t[1])
			elif type(redis_set_ops_results[ key ]) is list:
				yield (key, t[0], redis_set_ops_results[ key ].count(t[1]) )


# depreciated:
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

#### ------------------------------------------
#### Database Functions
#### - Clean
#### ------------------------------------------

def redis_data_masters_files(results_dict,redis_hosts):
	
	global new_attrs
	
	# -- PIPELINED REDIS OPERATIONS --------------------------
	r_masters_id, r_artists_id, r_meta_filter, r_meta_unique, r_videos = redis_hosts
	discogs_id, redis_set_ops_results = results_dict.pop('masters_id')[0], {'meta_filt':[]}
	actual_metadata = { 'genre' : results_dict['genre']	, 'style' : results_dict['style'], 'year' : results_dict['year'] }
	
	pipelines = [i.pipeline() for i in redis_hosts]
	
	# ---- Sets
	
	# 1. genre / style / year attributes per master id
	# 2. unique attributes cache
	# 3. release_title : masters_id
	# 4. artist-name : masters_id
	# 5. masters_id : video_urls
	
	for key,item in redis_add_attributes_gen(actual_metadata):
		redis_set_ops_results['meta_filt'].append( r_meta_filter.sadd( key+':'+item,discogs_id ) )
		new_attrs += r_meta_unique.sadd('unique:'+key,item)
	
	redis_set_ops_results['vids'] = [r_videos.sadd( discogs_id , video) for video in results_dict.pop('video_url')]
	
	# TODO release + artist to sorted set so can use ZRANGEBYLEX function for autocomplete
	redis_set_ops_results['release'] = r_masters_id.sadd( results_dict.pop('release_title')[0] , discogs_id)
	redis_set_ops_results['artist'] = [r_artists_id.sadd( artist , discogs_id) for artist in results_dict.pop('artist_name')]
	
	# - execute above redis ops for all hosts then garbage collect
	
	execs = [ i.execute() for i in pipelines]
	
	return discogs_id, redis_set_ops_results

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

def mongo_cli(db_dict):
	m = pymongo.MongoClient(db_dict['host'],db_dict['port'])
	db = m[db_dict['db']]
	c = db[db_dict['coll']]
	return c

def connection_set_up(mongo_collection_string):
	
	# -- SET UP DATABASE CONNECTIONS & RUNTIME VARIABLES ---
	
	# - Set up the redis db connections
	prints('Setting up Redis connections')
	redis_conn_dict = ( \
			{ 'host' : 'redis-masters-ids' , 'port' : 6379 } \
			, { 'host' : 'redis-artists-ids' , 'port' : 6379 } \
			, { 'host' : 'redis-metadata-filtering' , 'port' : 6379 } \
			, { 'host' : 'redis-metadata-unique' , 'port' : 6379 } \
			, { 'host' : 'redis-videos-masters' , 'port' : 6379 } \
			)
	
	hosts = [redis.Redis( host=conn['host'], port=conn['port'] ) for conn in redis_conn_dict]
	redis_connections_check(redis_conn_dict,hosts)
	
	# - Set up mongo db connections
	
	prints('Setting up Mongo connection')
	
	mongo_conn_dict = \
						{ \
							'host' : 'mongo-discogs-'+mongo_collection_string+'-api-service' \
							, 'port': 27017 \
							, 'db' : 'discogs' \
							, 'coll' : mongo_collection_string \
						}
						
	mongo_collection = mongo_cli( mongo_conn_dict )
	prints('Connected to Mongo host: ' + mongo_conn_dict['host'])
	prints('Connected to Mongo collection: ' + mongo_conn_dict['coll'])
	prints('There are currently '+ str(mongo_collection.count()) +' documents in the '+mongo_collection_string+' collection')
	
	#waiter(mongo_collection)
	
	return mongo_collection, hosts

#### ------------------------------------------
#### Helper functions
#### Clean up code &/ help paramaterize
#### ------------------------------------------

def metadata_helper(selection):
	if selection == 'masters':
		metadata_tags = [ 
							'genre' \
							,'style' \
							,'year' \
							,'release_title' \
							,'masters_id' \
							,'video_url' \
							,'artist_id' \
							,'artist_name' \
						]
						#,'video_title' \
						#,'artist_role' \
	return metadata_tags
	
def argaparser_function():
	parser = argparse.ArgumentParser(description='Get data from mongo master collection and load into redis')
	parser.add_argument('--verbose','-v',action='store_true')
	parser.add_argument('--data_quality',choices=['Accepted','Needs Vote',"Correct"])
	parser.add_argument('--mongo-collection',choices=['labels','masters','releases','artists'])
	return parser.parse_args()

#### ------------------------------------------
#### Logging Functions
#### - interpreter/stdout stats printing
#### ------------------------------------------

def sets_ign_logging(dictionary, discogs_id):
	for key,values in dictionary.items():
		if type(values) is int:
			if values == 0:
				#t = dt.now().strftime('%Y%m%d-%H-%M-%S')
				t = dt.now().strftime('%Y%m%d')
				with open('/logging/'+str(key)+'_ign_log'+t+'.txt','a') as f:
					f.write(discogs_id +'\n')
		elif type(values) is list:
			if 0 in values:
				t = dt.now().strftime('%Y%m%d')
				with open('/logging/'+str(key)+'_ign_log'+t+'.txt','a') as f:
					f.write(discogs_id +'\n')
			
def hashes_ign_logging(dictionary, discogs_id):
	for key,values in dictionary.items():
		if values is False:
			t = dt.now().strftime('%Y%m%d-%H-%M-%S')
			with open('/logging/'+str(key)+'_ign_log'+t+'.txt','a') as f:
				f.write(discogs_id +'\n')

def console_printer_gen(dictionary):
	for key_1,values in dictionary.items():
		for key_2,value in values.items():
			yield value

def console_string_gen(dictionary):
	for key_1,values in dictionary.items():
		key_2,key_3 = values.keys()
		yield (key_1,key_2,key_3)

#### ------------------------------------------
#### Runtime
#### ------------------------------------------

def main(args):
	
	"""
	1. Open a redis connection
	2. Open connection to masters collection
	3. Parse through the collection getting required bits
	4. Add the required lists to redis
	
	TODO
	"""
	
	starttime = dt.now()
	
	collection_name = 'masters' # args.mongo_collection
	
	mongo_collection, redis_hosts = connection_set_up(collection_name)
	
	prints('Database connections set up...\nIterating through documents...')

	insert_stats = { key : {'add' : 0 , 'ign' : 0} for key in ['release','artist','vids','meta_filt'] }
	
	global new_attrs
	new_attrs, empty_video_master = 0,0
	
	dataset = mongo_collection.find()
	
	for idx, master in enumerate(dataset):

		# - recursively traverse through each document, find all the required tags and their values
		
		metadata_tags = metadata_helper(collection_name)
		results_dict = { i : [] for i in metadata_tags }
		
		for tag in metadata_tags:
			for value in recursive_gen(master,tag,0):
				results_dict[tag].append(value)
				
		# - skip iteration no video links - no point processing
		
		if len(results_dict['video_url']) == 0:
			empty_video_master += 1
			pass
		
		#print('\n','res_dict',results_dict,'\n')
		#print('\nid',results_dict['masters_id'],'\n')
		#exit()		
		
		# - REDIS PIPELINE OPERATIONS

		if collection_name is 'masters':
			discogs_id, redis_set_ops_results = redis_data_masters_files(results_dict,redis_hosts)
		
		del metadata_tags, results_dict

		# -- STATS AND LOGGING -------------------------
		
		# - update stats dictionary redis insert results
		
		for key, result, value in sets_stats_gen( redis_set_ops_results ):
			insert_stats[ key ][ result ] += value
		
		sets_ign_logging( redis_set_ops_results, discogs_id )
		
		del discogs_id, redis_set_ops_results
		
		# - print information to stdout (bash)
		
		stats_str = ''.join([ \
								'\r+ {}/{} - {} new attrs - empt vid {} - ' \
								,' - '.join( \
											[ \
												key_1+''.join([' {} '+key_2+' {} '+key_3]) \
													for key_1,key_2,key_3 in console_string_gen(insert_stats)]) \
								,' +' \
							])
				
		console.write(stats_str.format( \
										idx+1 \
										, mongo_collection.count() \
										, new_attrs \
										, empty_video_master \
										, *[value for value in console_printer_gen(insert_stats)] \
									))
		console.flush()
		
	# ------------------------------------------
	
	prints('\nParsing complete!')
	elapsed_time = dt.now() - starttime
	prints('time taken (mins): '+str(elapsed_time.total_seconds()//60))
		
if __name__ == '__main__':
	args = argaparser_function()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)