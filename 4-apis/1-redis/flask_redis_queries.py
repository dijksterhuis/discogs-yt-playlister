#!flask/bin/python
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
import json, os, datetime, time, redis, werkzeug, requests, flask

# TODO - pip install flask-httpauth

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

def get_redis_metadata(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

app = Flask(__name__)

auth = HTTPBasicAuth()

redis_conn_dict = ( \
		{ 'host' : 'redis-metadata-master-ids' , 'port' : 6379 } \
		, { 'host' : 'redis-metadata-unique' , 'port' : 6379 } \
		, { 'host' : 'redis-videos-masters' , 'port' : 6379 } \
		, { 'host' : 'redis-artists-masters' , 'port' : 6379 } \
		, { 'host' : 'redis-artists-search' , 'port' : 6379 } \
		, { 'host' : 'redis-releasetitle-masters' , 'port' : 6379 } \
		)

hosts = [redis.Redis( host=conn['host'], port=conn['port'] ) for conn in redis_conn_dict]

redis_connections_check(redis_conn_dict,hosts)

r_attrs_id, r_unique_attrs, r_videos_masters, r_artists_masters, r_artist_search, r_reltitle_masters = hosts


@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@app.route('/am_i_alive', methods=['GET'])
def check_if_alive():
	return jsonify({'status': 'yes! I am!' })

@app.route('/wide-query', methods=['POST'])
def run_query():
	if not request.json:
		abort(400)
	else:		
		query_dict = dict(request.json)
		
		"""
		query_dict for wide -- {'year': [], 'genre': [], 'style': ['Big Band']}
		"""
		
		masters_pipe = r_masters.pipeline()
		
		master_ids_dict = { key : \
									set.union( \
										*[ r_masters.smembers(key+':'+value) for value in values ] \
									) \
								for key,values in query_dict.items() \
								if len(values) != 0 \
							}
				
		masters_pipe.execute()
		
		intersections = set.intersection(*master_ids_dict.values())
		
		videos_pipe = r_videos.pipeline()
		
		videos_dict = { attribute : \
								r_videos.hmget( \
									str( master_id.decode('utf-8') , attribute ) \
							for attribute in ['url','title'] \
							for master_id in intersections \
						}
		
		videos_pipe.execute()
			
		return jsonify(videos_dict), 201

@app.route('/artists-query', methods=['POST'])
def run_query():
	if not request.json:
		abort(400)
	else:		
		# TODO
		print('no data yet!')	
		return jsonify({'url' : 'No data yet!' , 'title' : 'no data yet!' }), 201


if __name__ == '__main__':
	app.run(debug=True)

