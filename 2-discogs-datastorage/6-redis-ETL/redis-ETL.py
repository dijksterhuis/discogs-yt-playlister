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

#def print(string):
#	if verbose_bool is True:
#		print(string)

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

def waiter(masters_coll):

	print('Checking if mongo is being updated, give me 30 seconds...')

	count_1 = masters_coll.count()
	time.sleep(30)
	count_2 = masters_coll.count()

	if count_2 != count_1:
		print('Seems that mongo is being updated, entering a waiting routine...')
		waiting_count = 0
		while (count_2 != count_1):
			if (waiting_counter % 5) == 0:
				print('Mongo still updating. Waiting. Waited for ' + str(waiting_count) + ' minutes')
			count_1 = masters_coll.count()
			time.sleep(60)
			count_2 = masters_coll.count()
			waiting_count += 1
	else:
		print('Seems that mongo is not being updated, continuing...')

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
		print('Redis servers pinged successfully!')
		return True

def star_dict_unpack(**argdict):
	return(argdict)

def sets_ign_logging(dictionary, discogs_id):
	for key,values in dictionary.items():
		if 0 in values or values is 0:
			t = dt.now().strftime('%Y%m%d-%H-%M-%S')
			with open('/logging/'+str(key)+'_ign_log'+t+'.txt','a') as f:
				f.write(discogs_id +'\n')

def hashes_ign_logging(dictionary, discogs_id):
	for key,values in dictionary.items():
		if values is False:
			t = dt.now().strftime('%Y%m%d-%H-%M-%S')
			with open('/logging/'+str(key)+'_ign_log'+t+'.txt','a') as f:
				f.write(discogs_id +'\n')

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
			yield (key, t[0], t[1])

def console_printer_gen(dictionary):
	for key_1,values in dictionary.items():
		for key_2,value in values.items():
			yield value

def console_string_gen(dictionary):
	for key_1,values in dictionary.items():
		key_2,key_3 = values.keys()
		yield (key_1,key_2,key_3)
	
def main(args):
	
	"""
	1. Open a redis connection
	2. Open connection to masters collection
	3. Parse through the collection getting required bits
	4. Add the required lists to redis
	
	TODO
	"""
	
	starttime = dt.now()
	
	# -- SET UP DATABASE CONNECTIONS & RUNTIME VARIABLES ---
	
	# - Set up the redis db connections
	print('Setting up Redis connections')
	redis_conn_dict = ( \
							{ 'host' : 'redis-hash-ids' , 'port' : 6379 } \
							, { 'host' : 'redis-metadata-filtering' , 'port' : 6379 } \
							, { 'host' : 'redis-metadata-unique' , 'port' : 6379 } \
							, { 'host' : 'redis-video-id-urls' , 'port' : 6379 } \
						)
	
	hosts = [redis.Redis( host=conn['host'], port=conn['port'] ) for conn in redis_conn_dict]
	r_hash_id, r_meta_filter, r_meta_unique, r_videos = hosts
	print(redis_conn_dict)
	print(hosts)
	redis_connections_check(redis_conn_dict,hosts)
	
	# - Set up mongo db connections
	
	print('Setting up Mongo connection')
	
	mongo_masters_conn_dict = { 'host' : 'mongo-discogs-masters' , 'port': 27017 , 'db' : 'discogs' , 'coll' : 'masters' }
	mongo_releases_conn_dict = { 'host' : 'mongo-discogs-releases' , 'port': 27017 , 'db' : 'discogs' , 'coll' : 'releases' }
						
	mongo_masters_collection = mongo_cli( mongo_masters_conn_dict )
	print('Connected to Mongo host: ' + mongo_masters_conn_dict['host'])
	print('Connected to Mongo collection: ' + mongo_masters_conn_dict['coll'])
	
	# - variable set up
	# @src is video link tag
	# name is artist name tag
	# title is video title
	# release-title is release title
	# item_id is the master id
	# artist_id is the artist_id
	
	metadata_tags = [ 'genre' ,'style' ,'year' ,'release_title' ,'masters_id' ,'video_url' ,'video_title' ,'artist_id' ,'artist_name' ,'artist_role' ]
	stats_keys = ['hash-release','hash-artist','meta_filt','meta-uniq','vids']
	insert_stats = { key : {'add' : 0 , 'ign' : 0} for key in stats_keys }
	new_attrs , empty_video_master = 0, 0
	dataset = mongo_masters_collection.find()
	
	print('There are currently '+ str(mongo_masters_collection.count()) +' documents in the '+mongo_masters_conn_dict['coll']+' collection')
	print('Iterating through documents...')
	# - wait until mongo has stopped updating to perform inserts
	
	#waiter(mongo_masters_collection)

	# -- START PROCESSING MONGO DOCUMENTS --------------
	for idx, master in enumerate(dataset):
		
		#results_dict = { i : [] for i in metadata_tags}
		redis_hash_ops_results, redis_set_ops_results = dict(), {'meta_filt':[]}
		
		# - recursively traverse through each document, find all the required tags and their values
		
		#for tag in metadata_tags:
		#	for value in recursive_gen(master,tag,0):
		#		results_dict[tag].append(value)
		
		# testing!
		
		results_dict = { tag : [ value for value in recursive_gen(master,tag,0) ] for tag in metadata_tags}
				
		# - skip if no video links - no point processing
		
		if len(results_dict['video_url']) == 0:
			empty_video_master += 1
			pass
		
		# - seperate out the id, video links/titles and artist names/ids
		
		print('\n',results_dict,'\n')
		
		discogs_id , release_title = results_dict.pop('masters_id')[0] , results_dict.pop('release_title')[0]
		videos_dict = {'video_title' : results_dict.pop('video_title') ,'video_url' : results_dict.pop('video_url') }
		artists_dict = { 'artist_name': results_dict.pop('artist_name'), 'artist_id': results_dict.pop('artist_id'), 'artist_role': results_dict.pop('artist_role') }
						
		# -- REDIS OPERATIONS --------------------------
		
		pipelines = [ i.pipeline() for i in hosts]
		
		# ---- Sets
		
		# 1. genre / style / year attributes per master id
		# 2. unique attributes cache
		# 3. video url data
		
		for key,item in redis_add_attributes_gen(results_dict):
			redis_set_ops_results['meta_filt'].append( r_meta_filter.sadd( key+':'+item,discogs_id ) )
			new_attrs += r_meta_unique.sadd('unique:'+key,item)
		for video_name, video_url in videos_dict.items():
			redis_hash_ops_results['vids'] = r_videos.sadd( discogs_id , video_url )
			
		# ---- Hashes
		
		# - insert an entity's searchable hash data
		# index: id type (release ?, label, master, artist)
		# fields: name (value: James Holden) , id (value: 119429)
		# TODO Lables - needs the releases mongo collection

		#redis_hash_ops_results['hash-labels'] = r_hash_id.hmset('label' ,{'label-id' : TODO ,'label-name' : TODO })		
		redis_hash_ops_results['hash-release'] = r_hash_id.hmset('release' ,{'master-id' : discogs_id,'release-title' : release_title })
		redis_hash_ops_results['hash-artist'] = [ r_hash_id.hmset( 'artist' , { 'artist-name' :  artists_dict['artist_name'][idx] , 'artist-id' :  artists_dict['artist_id'][idx] } ) \
													for idx, a in enumerate( artists_dict['artist_name']) ]
		
		execs = [ i.execute() for i in pipelines]
		
		# -- STATS AND LOGGING -------------------------
		# - log any master ids that have been ignored
		
		sets_ign_logging( redis_set_ops_results, discogs_id )
		hashes_ign_logging( redis_hash_ops_results, discogs_id )
		
		# - update stats dicts (added or not)
		# 1. set ops
		# 2. hash ops
		
		for key, result, value in sets_stats_gen( redis_set_ops_results ):
			insert_stats[ key ][ result ] += redis_set_ops_results[ key ].count( value )
		for key, result in hash_stats_gen( redis_hash_ops_results ):
			insert_stats[ key ][ result ] += 1
			
		# - print information to stdout
		# stats_str is fun!
		
		stats_str = ''.join( [ '\r+ {}/{} - {} new attrs - empt vid {} - ' ,' - '.join([key_1+''.join([' {} '+key_2+' {} '+key_3]) for key_1,key_2,key_3 in console_string_gen(insert_stats)]) ,' +' ])
		console.write(stats_str.format( idx+1, mongo_masters_collection.count(), new_attrs, empty_video_master, *[value for value in console_printer_gen(insert_stats)] ))
		console.flush()
	# ------------------------------------------
	print('\nParsing complete!')
	elapsed_time = dt.now() - starttime
	print('time taken (mins): '+str(elapsed_time.total_seconds()//60))
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get data from mongo master collection and load into redis")
	parser.add_argument('--verbose','-v',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)