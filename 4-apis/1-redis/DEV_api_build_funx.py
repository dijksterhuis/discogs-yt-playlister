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
	
	scards_dict, master_ids_dict = dict(), dict()
	
	redis_insts = { key : redis_meta_host(key) for key in metadata_filter_dict.keys() }
	
	print(redis_insts)
	
	for r in redis_inst.values():
		ping_check = redis_conn_check(r)
		if ping_check != True:
			return make_response( ping_check, 500 )
			
	pipes = [ r.pipeline() for r in redis_insts.values() ]
	
	if len(metadata_filter_dict.keys()) == 0:
		return make_json_resp( {'ERR' : 'No input data given '}, 400 )
		
	else:
		for key in metadata_filter_dict.keys():
			print('key',key)
			if len(metadata_filter_dict[key]) == 0:
				pass
			else:
				print('values',metadata_filter_dict.values())
				for value in metadata_filter_dict[key]:
					print('value -ids: ',get_redis_values(redis_insts[key],value))
				
				#scards_dict[key] = sum([ redis_insts[key].scard(value) for value in metadata_filter_dict[key] ])
				master_ids[key] = list(set.union(*[ get_redis_values(redis_insts[key],value) for value in metadata_filter_dict[key] ]))
				
	e = [ p.execute() for p in pipes ]
	
	return make_json_resp(master_ids , 200 )

def get_unique_metadata(tag):
	r = redis_meta_host(tag)
	
	ping_check = redis_conn_check(r)
	if ping_check != True:
		return make_response( ping_check, 500 )
	
	metadata = get_redis_keys(r).sort()
	print(metadata)
	return make_json_resp( metadata , 200)
