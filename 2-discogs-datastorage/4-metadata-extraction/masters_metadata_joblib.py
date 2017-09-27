#!/usr/local/bin/python
import json, argparse, redis, os
from joblib import Parallel,delayed
from sys import stdout as console
from sys import exit
from datetime import datetime as dt
"""
os import used for error codes on exits - could be useful for handling data problems at docker run time
see here: https://docs.python.org/2/library/os.html#process-management
"""

def prints(string):
	if verbose_bool is True:
		print(string)

def multi_tier_generator(masters_file,tags):
	
	"""
	Description + Pseudocode to go here...
	TODO
	Change log file paths (currently for local dev work)
	Description + Pseudocode
	"""
	
	with open('/logging/processed_ids.txt','a') as std_logs:
		with open('/logging/novalues_logfile.txt','a') as novalue_logs:
			assert (total > 0),"File shouldn't have length 0"
			total = len(masters_file)
			
			for idx, master_obj in enumerate(masters_file):
				for tag in tags:
					
					logs_string = 'file_idx|'+str(idx)+'|search_term|' + str(tag) + '|masterid|' + str(key) +'\n' 
					
					# ---- first tier
					if tag in master_obj.keys():
						yield ( tag , master_obj[ tag ] , master_obj["@id"] )
					
					# ---- second tier objects (nested)
					elif tag + 's' in master_obj.keys():
						for nested_obj in list(master_obj[ tag + 's' ].values() ):

							if tag == 'video':
								for video_idx, video in enumerate(nested_obj):
									yield ( tag , master_obj["@id"] , video['@src'] )
						
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
					
def main(args):
	
	"""
	1. Open a redis connection
	2. Open the masters file
	3. Parse through the file getting required bits
	4. Add the required lists to redis
	
	TODO
	1 - Change filepaths - jsons + loggin
	2 - How to handle data that only needs to be updated?
	3 - Change redis server connection string
	4 - secure redis?!
	"""
	starttime = dt.now()
	
	r = redis.Redis(host='redis-metadata-master-ids',port='6379')
	
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
		with Parallel(n_jobs=2) as parallel:
		joblib version - to test!
		r_io_list = Parallel(n_jobs=2,verbose=5)(delayed(r.sadd)(tag + ':' + key, value) \
					for tag,key,value in multi_tier_generator(masters,metadata_tags) )
		print('not added',r_io_list.count(0) )
		print('added',r_io_list.count(1) )
		print('total',len(r_io_list) )
		elapsed_time = starttime - dt.now()
		print('time taken: ',elapsed_time.total_seconds())
		
			
	except AssertionError:
		print('File has a length <= 0')
		exit()
	except KeyError:
		print("There was a key error...")
		exit()
	except IndexError:	
		print("There was a indexing error...")
		exit()
	except:
		print("An un-classified (non-captured exception) was raised, check traceback!")
		exit()
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get master release IDs per genre then add to Redis")
	parser.add_argument('masters_file',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)