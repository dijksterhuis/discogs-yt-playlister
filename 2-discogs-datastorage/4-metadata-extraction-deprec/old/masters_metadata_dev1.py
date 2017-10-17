#!/usr/local/bin/python3
import json, argparse, redis
from sys import stdout as console

def prints(string):
	if verbose_bool is True:
		print(string)

def dictionary_update(result, id_dict, master_id):
	if result not in id_dict.keys():
		id_dict[ result ] = [ master_id ]
	else:
		id_dict[ result ].append( master_id )

def one_tier_search(masters,search_term):
	"""
	Example:
	{@id = 2, Year = 2001}
	"""
	
	id_dict = dict()
	for master in masters:
		dictionary_update( master[ search_term ] , id_dict, master["@id"] )
	return id_dict

def two_tier_search(masters,search_term):
	
	"""
	Examples: 
	{@id = 2, Genres : {genre : electronic , genre: rock} }
	{@id = 2, styles : {style : house , style: techno} }
	"""
	
	#search_list = [ entry[ search_term_1 ][ search_term_2 ] for entry in masters ]
	#search_id_dict = { entry : [] for entry in search_list }
	
	id_dict = dict()
	for master in masters:
		results = list(master[ search_term ].values() )
		for result in results:
			dictionary_update(result, id_dict, master["@id"] )
	return id_dict

def one_tier_generator(masters_file,search_term):
	for master in masters:
		prints('one tier search search term present: ',search_term in masters.keys())
		yield { master[ search_term ] : master["@id"] }
	
def two_tier_generator(masters_file,search_term):
	for master in masters:
		prints('two tier search search term present: ',search_term in masters.keys())
		if search_term not in master.keys():
			break
		for result in list(master[ search_term ].values() ):
			yield { result : master["@id"] }
		
def multi_tier_generator(masters_file,tags):
	with open('./testing/logfile.txt','a') as logs:

		total = len(masters_file)
		
		for idx, master in enumerate(masters_file):
			for search_term in tags:
			
				if verbose_bool is True:
					console.write("\r{} of {} -- ".format(idx+1, total))
					console.flush()
				
				# first tier objects
			
				if search_term in master.keys():
					output = ( search_term , master[ search_term ] , master["@id"] )
			
				# second tier objects (nested)
				elif search_term + 's' in master.keys():
					for result in list(master[ search_term + 's' ].values() ):
						if search_term == 'video':
							for video_idx, video in enumerate(result):
								yield ( search_term , master["@id"] , video['@src'] )
						else:
							output = ( search_term , result , master["@id"] )
						
				# error capture
			
				else:
					prints('No search term present\n')
					logs.write('search_term|' + search_term + '|masterid|' + str(master["@id"]) +'|no value'+ '\n' )
					pass
				
				
				yield output
		
def main(args):
	
	"""
	1. Open a redis connection
	2. Open the masters file
	3. Parse through the file getting required bits
	4. Add the required lists to redis
	
	TODO
	
	Three different redis instances?
	How to handle the multi-dimensional request nature (Ids for specific year, style, genre)?
	3 - Can this be done on one file pass? Rather than 3?
	4 - How to handle data that only needs to be updated?
	
	"""
	
	#r = redis.Redis(host='redis-metadata-master-ids',port='6000')
	r = redis.Redis(host='localhost',port='6379')
	r.ping()
	
	with open(args.masters_file[0],'r') as infile:
		masters = json.load(infile)['masters']['master']
	
	metadata_tags = ['genre','style','year','video']
	for tag,key,value in multi_tier_generator(masters,metadata_tags):
		prints(str(tag) + ' ' + str(key) + ' ' + str(value))
		r.sadd(tag + ':' + key, value)
		counter = 1
	
	### Old version
	
	#ids_per_genre = two_tier_search(masters,'genre')
	#ids_per_style = two_tier_search(masters,'style')
	#ids_per_year = one_tier_search(masters,'year')
	
	#metadata = {'genre' : ids_per_genre , 'style' : ids_per_style , 'year' : ids_per_year }
	
	#for meta_key in metadata:
	#	for dict_key in metadata[meta]:
	#		for master_id in metadata[meta][dict_key]:
	#			r.sadd(meta_key + ':' + dict_key, master_id)
	
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get master release IDs per genre then add to Redis")
	parser.add_argument('masters_file',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)