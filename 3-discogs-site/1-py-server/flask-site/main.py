from flask import  Flask, render_template, redirect, url_for, request, session, flash
#from werkzeug import generate_password_hash, check_password_hash
import json, os, datetime, time, redis
#from werkzeug.datastructures import ImmutableOrderedMultiDict
import werkzeug

app = Flask(__name__)

# Super secret cookie session key
#app.secret_key = generate_password_hash(os.urandom(24))

# --------------------------------------------------

# app routes (pages and fucntions applied to server data etc.)

#r_videos = redis.Redis(host='redis-videos-masters',port=6379)
#r_unique = redis.Redis(host='redis-metadata-unique',port=6379)
#r_masters = redis.Redis(host='redis-metadata-master-ids',port=6379)
#
#r_unique_reldates = redis.Redis(host='redis-metadata-unique-reldate',port=6379)
#r_unique_year = redis.Redis(host='redis-metadata-unique-year',port=6379)
#r_unique_style = redis.Redis(host='redis-metadata-unique-style',port=6379)
#r_unique_genre = redis.Redis(host='redis-metadata-unique-genre',port=6379)

def redis_host(value):
	return redis.Redis(host='redis-metadata-unique-'+value,port=6379)

def get_redis_keys(redis_instance):
	return [i.decode('utf-8') for i in list(redis_instance.keys())]


def get_redis_values(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

@app.route('/',methods=['GET','POST'])
#@login_required
#@subscription_required
def wide_query():
	
	if request.method == 'GET':
		print('GET')
		
		# reldate?
		unique_params = { \
								tag : get_redis_keys(redis_host(tag)) \
									for tag in ['year','genre','style'] \
						}
		
		for key in unique_params:
			unique_params[key].sort()
		
		return render_template( \
									'/query-form.html', years=unique_params['year'] \
									, genres=unique_params['genre'], styles=unique_params['style'] \
								)
	
	## These can be big queries, so we want post requests, rather than a get rest API
	
	elif request.method == 'POST':
		
		print('POST')
		
		time_dict = { 0: ('start_time',datetime.datetime.now() ) } 
		wide_query_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in ['year','genre','style']}
		
		time_dict[1] = ('wide_query_dict_get' , datetime.datetime.now())
		
		print('getting: ',wide_query_dict)
		
		scards_dict, master_ids_dict, all_links = dict(), dict(), list()
		
		# get master IDs for wide filters
		
		for key in wide_query_dict.keys():
			if len(wide_query_dict[key]) == 0: pass
			else:
				p = redis_host(key).pipeline()
				for value in wide_query_dict[key]:
					scards_dict[key] = sum([ redis_host(key).scard(value) for value in wide_query_dict[key] ])
					master_ids_dict[key] = set.union(*[ redis_host(key).smembers(value) for value in wide_query_dict[key] ])
				p.execute()
		
		print('master ids gotten')
		
		print('cardinalities: ', scards_dict)
		
		time_dict[2] = ('scards and master-ids set' , datetime.datetime.now())
		
		intersections = set.intersection(*master_ids_dict.values())
		
		time_dict[3] = ('intersection_time_delta' , datetime.datetime.now())
		print('intersections gotten')
		
		videos_pipe = redis_host('redis-video-id-urls').pipeline()
		for i in intersections:
			links = get_redis_values(redis_host('redis-video-id-urls'),str(i.decode('utf-8')))
			if len(links) == 0:
				pass
			elif len(links) == 1:
				all_links.append(links[0])
			else:
				for link in links:
					all_links.append(link)
		videos_pipe.execute()
		print('videos gotten')
		tot = len(all_links)
		
		time_dict[4] = ('videos_time_delta' , datetime.datetime.now())
		
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
		return render_template('/results.html',intersex=all_links,total_count=tot)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5000)