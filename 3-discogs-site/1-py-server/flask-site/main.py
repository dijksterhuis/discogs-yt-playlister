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

r_videos = redis.Redis(host='redis-videos-masters',port=6379)
r_unique = redis.Redis(host='redis-metadata-unique',port=6379)
r_masters = redis.Redis(host='redis-metadata-master-ids',port=6379)

def get_redis_metadata(redis_instance,key_string):
	return [i.decode('utf-8') for i in list(redis_instance.smembers(key_string))]

@app.route('/',methods=['GET','POST'])
#@login_required
#@subscription_required
def films_cat():
	
	if request.method == 'GET':
		print('GET')
		
		unique_params = { tag : get_redis_metadata(r_unique,'unique:'+tag) for tag in ['year','genre','style']}
		
		for key in unique_params:
			unique_params[key].sort()
		
		#y = get_redis_metadata(r_unique,'unique:year')
		#g = get_redis_metadata(r_unique,'unique:genre')
		#s = get_redis_metadata(r_unique,'unique:style')
		#y.sort()
		#g.sort()
		#s.sort()
		
		print(unique_params)
		return render_template('/query-form.html',years=unique_params['year'],genres=unique_params['genre'],styles=unique_params['style'])
		
	
	## These can be big queries, so we want post requests, rather than a get rest API
	
	elif request.method == 'POST':
			
		max_dict = { 'max_'+tag : len(get_redis_metadata(r_unique,'unique:'+tag)) for tag in ['year','genre','style']}
		print(max_dict)
		
		print('POST')
		
		time_dict = { 0: ('start_time',datetime.datetime.now() ) } 
		
		form_dict = { tag : request.form.getlist('query:'+tag, type=str) for tag in ['year','genre','style']}
		
		#years = request.form.getlist('queryYear')
		#genres = request.form.getlist('queryGenre')
		#styles = request.form.getlist('queryStyle')
		
		print('getting: ',form_dict)
		
		
		###### TODO - This need to be more elegant
		# ---- logic to ignore selecting "Full" parameter selections 
		# ---- (they don't matter)
		
		query_dict = dict()
		
		for key,value in form_dict.items():
			if len(value) == max_dict['max_'+key] or len(value) == 0:
				print('not gonna bother looking at '+key+' data')
				query_dict[key] = False
			else:
				query_dict[key] = True
		
		time_dict[1] = ('prepare_query_time' , datetime.datetime.now())
		
		# ---- Redis ops to get all the relevant master release ids for chosen filters
		# - get sets for each filter parameter value (can be multiple choices)
		# - Union the results for each parameter
		# - Intersect the results
		# ---- TODO
		# - This takes around 5 seconds for a larger query (2015-2017, electronic, acid)
		# - How could these be reduced? Sorting the sets in redis?
		
		cards_dict = dict()
		
		totals_pipe = r_masters.pipeline()
		
		for key,value in query_dict.items():
			if value is True:
				cards_dict[key] = sum([r_masters.scard(key+':'+i) for i in form_dict[key] ])
		
		totals_pipe.execute()
		
		print('set cardinalities: ',cards_dict)
		time_dict[2] = ('get_totals_delta' , datetime.datetime.now())
		
		master_ids_dict = dict()
		
		masters_pipe = r_masters.pipeline()
		
		for key,value in query_dict.items():
			if value is True:
				master_ids_dict[key] = set.union(*[r_masters.smembers(key+':'+i) for i in form_dict[key] ])
		
		
		#years_unioned = set.union(*[r_masters.smembers('year:'+i) for i in years])
		#genre_unioned = set.union(*[r_masters.smembers('genre:'+i) for i in genres])
		#styles_unioned = set.union(*[r_masters.smembers('style:'+i) for i in styles])
				
		masters_pipe.execute()
		
		time_dict[3] = ('masters_query_delta' , datetime.datetime.now())
		
		intersections = set.intersection(*master_ids_dict.values())
		
		time_dict[4] = ('intersection_time_delta' , datetime.datetime.now())
		
		all_links = list()
		
		videos_pipe = r_videos.pipeline()
		
		for i in intersections:
			links = get_redis_metadata(r_videos,'videos:'+str(i.decode('utf-8')))
			if len(links) == 0:
				pass
			elif len(links) == 1:
				all_links.append(links[0])
			else:
				for link in links:
					all_links.append(link)
					
		videos_pipe.execute()
		
		tot = len(all_links)
		
		time_dict[5] = ('videos_time_delta' , datetime.datetime.now())
		
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