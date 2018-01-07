from flask import  Flask, render_template, redirect, url_for, request, session, flash
#from werkzeug import generate_password_hash, check_password_hash
import json, os, datetime, time, redis
#from werkzeug.datastructures import ImmutableOrderedMultiDict
import werkzeug
from youtube_playlist_gen import create_playlist, insert_videos

app = Flask(__name__)

# Super secret cookie session key
#app.secret_key = generate_password_hash(os.urandom(24))

# --------------------------------------------------

# app routes (pages and fucntions applied to server data etc.)

def redis_meta_host(value):
	return redis.Redis(host='redis-metadata-unique-'+value,port=6379)

def redis_host(value):
	return redis.Redis(host=value,port=6379)

def get_redis_keys(redis_instance):
	return [i.decode('utf-8') for i in list(redis_instance.keys())]

def get_redis_values(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

@app.route('/',methods=['GET','POST'])
#@login_required
#@subscription_required
def wide_query():
	
	if request.method == 'GET':
		print('GET',request)
		
		# reldate?
		tags = ['year','genre','style']
		#uniq_params = { tag : request.get('/unique_metadata',json=jsonify( {'tag':tag} )) for tag in tags }
		uniq_params = { tag : get_redis_keys(redis_meta_host(tag)) for tag in tags }
		for key in uniq_params: uniq_params[key].sort()
		
		return render_template('/query-form.html',years=uniq_params['year'],genres=uniq_params['genre'],styles=uniq_params['style'])
	
	## These can be big queries, so we want post requests, rather than a get rest API
	
	elif request.method == 'POST':
		
		print('POST',request)
		
		time_dict = { 0: ('start_time',datetime.datetime.now() ) } 
		wide_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in ['year','genre','style']}
		
		artist_name = request.form.getlist('search:artist_name')[0]
		release_name = request.form.getlist('search:release_name')[0]
		label_name = request.form.getlist('search:label_name')[0]
		
		print(artist_name,release_name,label_name)		
		
		# -------- TODO API
		
		artist_ids = set(get_redis_values(redis_host('redis-artists-ids'),artist_name))
		release_ids = set(get_redis_values(redis_host('redis-masters-ids'),release_name))
		#label_ids = set(get_redis_values(redis_host('redis-label-ids'),release_name))
		
		#artist_ids = request.get('/artist_name_ids',json=jsonify( {'name':artist_name} ))
		#release_ids = request.get('/release_name_ids',json=jsonify( {'name':artist_name} ))
		#label_ids = request.get('/label_name_ids',json=jsonify( {'name':label_name} ))
		print(artist_ids,release_ids) #, label_ids
		
		time_dict[1] = ('wide_query_dict_get' , datetime.datetime.now())
		
		print('getting: ',wide_query_dict)
		
		scards_dict, master_ids_dict, all_links = dict(), dict(), list()
		#/metadata_ids
		# get master IDs for wide filters
		if len(wide_query_dict.keys()) != 0:
			for key in wide_query_dict.keys():
				if len(wide_query_dict[key]) == 0: pass
				else:
					# -------- TODO API
					p = redis_meta_host(key).pipeline()
					for value in wide_query_dict[key]:
						#request.get('/metadata_ids',json=jsonify( {key : value} ))
						scards_dict[key] = sum([ redis_meta_host(key).scard(value) for value in wide_query_dict[key] ])
						master_ids_dict[key] = set.union(*[ redis_meta_host(key).smembers(value) for value in wide_query_dict[key] ])
					p.execute()
		
		print('master ids gotten')
		
		print('cardinalities: ', scards_dict)
		
		time_dict[2] = ('scards and master-ids set' , datetime.datetime.now())
		
		# ---- TODO - and/or logic - intersections
		
		intersections = set.intersection(set(*master_ids_dict.values()))
		time_dict[3] = ('intersection_time_delta' , datetime.datetime.now())
		print('intersections gotten')
		
		# ---- TODO - and/or logic - unions
		
		lets_union_u = [artist_ids, release_ids, intersections]
		if sum([len(i) for i in lets_union_u]) != 0: unions = set.union( *[i for i in lets_union_u if len(i) > 0] )
		else: return render_template('/no_results.html')
		time_dict[4] = ('union_time_delta' , datetime.datetime.now())
		
		print('unions gotten')
		print('total video links to get: ',len(unions))
		
		# ---- VIDEOS GET
		
		# -------- TODO API
		
		#request.get('/video_urls',json=jsonify( unions ))
		
		videos_pipe = redis_host('redis-video-id-urls').pipeline()

		for master_id in unions:
			if isinstance(master_id,bytes): master_id = str(master_id.decode('utf-8'))
			links = get_redis_values(redis_host('redis-video-id-urls'),master_id)
			if len(links) == 0: pass
			elif len(links) == 1 and type(links) is list: all_links.append(links[0])
			elif isinstance(links,list):
				for link in links: all_links.append(link)
			else: pass
			
		videos_pipe.execute()
		print('videos gotten')

		time_dict[5] = ('videos_time_delta' , datetime.datetime.now())
		tot = len(all_links)
		
		# ---- ARTIST NAME GET
		#
		#artists = list()
		#artist_pipe = redis_host('redis-mastersid-artistname').pipeline()
		#
		#for i in intersections:
		#	links = get_redis_values(redis_host('redis-mastersid-artistname'),str(i.decode('utf-8')))
		#	if len(links) == 0: pass
		#	elif len(links) == 1 and type(links) is list: artists.append(links[0])
		#	elif type(links) is list:
		#		for link in links: artists.append(link)
		#	else: pass
		#	
		#artist_pipe.execute()
		#print('artists gotten')
		#time_dict[6] = ('artists_time_delta' , datetime.dßatetime.now())
		#
		## ---- RELEASE TITLE GET
		#
		#release_title_pipe = redis_host('redis-masterids-titles').pipeline()
		#titles = [ get_redis_values(redis_host('redis-masterids-titles'),str(i.decode('utf-8'))) for i in intersections]
		#release_title_pipe.execute()
		#print('titles gotten')
		#time_dict[7] = ('release_names_delta' , datetime.datetime.now())
		
		# ---- TIMINGS TEST OUTPUT
		
		print('\ntimings: key, time since start, time since last op, str_key')
		for time_key,time_value in time_dict.items():
			if time_key is 0:
				print(time_key  , 0 , 0  , time_value[0] )
			else:
				from_start = time_value[1] - time_dict[0][1]
				from_last_op = time_value[1] - time_dict[time_key-1][1]
				print(time_key , from_start , from_last_op , time_value[0] )
		total_time = datetime.datetime.now() - time_dict[0][1]
		print('\ntotaltime',total_time.total_seconds())
		print('\n')
		
		# TODO !!!
		session_id = 1
		
		redis_query_cache_adds = sum( [ redis_host('discogs-session-query-cache').sadd(session_id, \
													link.replace('https://youtube.com/watch?v=','') ) for link in all_links ] )
		redis_host('discogs-session-query-cache').expire(session_id,30*60)
		
		return render_template('/added.html',intersex=all_links,total_count=tot)

@app.route('/create_playlist',methods=['GET'])
def send_to_yt():
	title = request.form.get('playlist_title')
	desc = request.form.get('playlist_desc')
	session_id = 1
	
	r = redis_host('discogs-session-query-cache')
	video_ids = list(r.smembers(session_id))
	
	playlist_result = create_playlist(title,desc)
	for video_id in video_ids:
		insert_videos( playlist_result , video_id)

if __name__ == '__main__':
	#app.run(host='0.0.0.0',debug=True,port=5000)
	app.run(host='0.0.0.0',debug=False,port=80)