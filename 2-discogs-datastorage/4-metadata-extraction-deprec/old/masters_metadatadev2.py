#!/usr/local/bin/python3
import json, argparse, redis, os
from joblib import Parallel,delayed
from sys import stdout as console
from sys import exit
"""
os import used for error codes on exits - could be useful for handling data problems at docker run time
see here: https://docs.python.org/2/library/os.html#process-management
"""

def prints(string):
	if verbose_bool is True:
		print(string)

def multi_tier_generator(masters_file,tags):
	
	with open('./testing/processed_ids.txt','a') as std_logs:
		with open('./testing/novalues_logfile.txt','a') as novalue_logs:
			assert (total > 0),"File shouldn't have length 0"
			total = len(masters_file)
			
			for idx, master in enumerate(masters_file):
				for search_term in tags:
					
					logs_string = 'file_idx|'+str(idx)+'|search_term|' + str(tag) + '|masterid|' + str(key) +'\n' 
					
					# ---- first tier
					if search_term in master.keys():
						output = ( search_term , master[ search_term ] , master["@id"] )
					
					# ---- second tier objects (nested)
					elif search_term + 's' in master.keys():
						for result in list(master[ search_term + 's' ].values() ):
							if search_term == 'video':
								for video_idx, video in enumerate(result):
									yield ( search_term , master["@id"] , video['@src'] )
							else:
								output = ( search_term , result , master["@id"] )
					
					# ---- missing values & general process logging
					else:
						novalue_logs.write(logs_string)
						pass
					std_logs.write(logs_string)
					
					# ---- print process status info
					if verbose_bool is True:
						console.write("\r{} of {} -- ".format(idx+1, total))
						console.flush()
						
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
	if r.ping() is not True:
		print('Could not connect to the Redis Server, quitting')
		#os.EX_NOHOST
		exit(68)
	try:
		with open(args.masters_file[0],'r') as infile:
			masters = json.load(infile)['masters']['master']
	except IOError:
		print("Error: can't find file or read data")
		#os.EX_NOINPUT
		exit(66)
	except MemoryError:
		print("Memory Error!")
		exit()

	try:
		metadata_tags = ['genre','style','year','video']
		for tag,key,value in multi_tier_generator(masters,metadata_tags):
			prints(str(tag) + ' ' + str(key) + ' ' + str(value))
			r_io = r.sadd(tag + ':' + key, value)
			if r_io != 1:
				print('VALUES NOT ADDED: ' + str(tag) + ' ' + str(key) + ' ' + str(value))
		#with Parallel(n_jobs=2) as parallel:
		#joblib version - to test!
		#r_io_list = Parallel(n_jobs=2,verbose=5)(delayed(r.sadd)(tag + ':' + key, value) \
		#			for tag,key,value in multi_tier_generator(masters,metadata_tags) )
		#print('not added',r_io_list.count(0) )
		#print('added',r_io_list.count(1) )
		#print('total',len(r_io_list) )
			
	except AssertionError:
		print('File has a length <= 0')
	except KeyError:
		print("There was a key error...")
	except IndexError:	
		print("There was a indexing error...")
	#except LookupError:
	#	print("There's an key/indexing issue...")
	#except GeneratorExit:
	#	print('Generator exited...')
	#	print('Last master id processed: ' +str(key))
	except:
		print("An un-classified (non-captured exception) was raised, check traceback!")
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get master release IDs per genre then add to Redis")
	parser.add_argument('masters_file',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)