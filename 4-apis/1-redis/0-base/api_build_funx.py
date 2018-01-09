import redis, datetime, time
from flask import make_response, jsonify
from webargs import fields

#### WEBARGS ARG DEfs:

NAME_ARGS = { 'name_type' : fields.Str(required=True), 'name': fields.Str(required=True) }
TAG_ARGS = { 'tag' : fields.Str(required=True) }
VIDEO_ARGS = { 'master_ids' : fields.List(fields.Str(required=True)) }
METADATA_ID_ARGS = { 'year' : fields.List(fields.Str(required=True)) \
						, 'style' : fields.List(fields.Str(required=True))\
						, 'genre' : fields.List(fields.Str(required=True)) \
					}
V_CACHE_ARGS = { 'session_id' : fields.Str(required=True) , 'video_ids' : fields.List(fields.Str()) }


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

def get_videos(master_ids_list):
	
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

def get_metadata_ids(metadata_filter_dict):
	
	print(metadata_filter_dict)
	
	master_ids = dict()
	#scards = dict()
	
	redis_insts = { key : redis_meta_host(key) for key in metadata_filter_dict.keys() }
	
	print(redis_insts)
	
	for r in redis_insts.values():
		ping_check = redis_conn_check(r)
		if ping_check != True:
			return make_response( ping_check, 500 )
			
	if len(metadata_filter_dict.keys()) == 0:
		return make_json_resp( {'ERR' : 'No input data given '}, 400 )
		
	else:
		pipes = [ r.pipeline() for r in redis_insts.values() ]
		
		for key in metadata_filter_dict.keys():
			print('key',key)
			if len(metadata_filter_dict[key]) == 0:
				pass
			else:
				print('values',metadata_filter_dict.values())
				master_ids[key] = set()
				for value in metadata_filter_dict[key]:
					r_vals = get_redis_values(redis_insts[key],value)
					master_ids[key] = set.union(master_ids[key],r_vals)
				master_ids[key] = list(master_ids[key])
				
				#scards[key] = sum([ redis_insts[key].scard(value) for value in metadata_filter_dict[key] ])
				
	e = [ p.execute() for p in pipes ]
	
	return make_json_resp(master_ids , 200 )

def get_unique_metadata(tag):
	r = redis_meta_host(tag)
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	metadata = get_redis_keys(r)
	metadata.sort()
	print(metadata)
	return make_json_resp( metadata , 200)

def put_video_ids_cache(session_id,video_ids_list):
	r = redis_host('discogs-session-query-cache')
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	stripped_videos = [ video.lstrip('https://www.youtube.com/watch?v=') for video in video_ids_list ]
	result = sum([ r.sadd(session_id, video) for video in stripped_videos ])
	redis_host('discogs-session-query-cache').expire(session_id,30*60)
	
	return make_json_resp(result,200)
	
def get_video_ids_cache(session_id):
	
	r = redis_host('discogs-session-query-cache')
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	result = get_redis_values(r,session_id)
	
	return make_json_resp(result,200)


def clear_video_ids_cache(session_id):
	
	r = redis_host('discogs-session-query-cache')
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	result = r.delete(session_id)
	
	return make_json_resp(result,200)
	
def clear_video_ids_cache(session_id):

	r = redis_host('discogs-session-query-cache')

	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	keys = [k.lstrip('query:') for k in get_redis_keys(r)]
	result = 'query:'+str(max(keys))

	return make_json_resp(result,200)