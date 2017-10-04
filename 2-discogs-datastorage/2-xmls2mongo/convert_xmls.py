#!/usr/local/bin/python

import xmltodict, json, argparse, re, os
from sys import stdout as console
from pymongo import MongoClient

def prints(string):
	"""
	Print the string if verbosity (argparse arg) is true
	"""
	if verbose_bool is True:
		print(string)

def io_err():
	prints("Error: can't find file or read data")
	#os.EX_NOINPUT
	exit(66)
def mem_err():
	prints("Memory Error!")
	exit()
def misc_err():
	prints("An unknown error occured, check traceback")
	exit()

def mongo_cli(db_dict):
	"""
	Set up a connection to a mongo database using an input dictionary
	Also return the result of a ping command sent to the database
	input - db_dict = {'host' : 'mongo-discogs', 'port': 27017 , 'db' : 'discogs' , 'coll' : collection }
	outputs - (collection , ping result)
	"""
	
	mongo = MongoClient(db_dict['host'],db_dict['port'])
	db = mongo[db_dict['db']]
	db.drop_collection(db_dict['coll'])
	collection = db[db_dict['coll']]
	return (collection , mongo[db_dict['db']].command('ping') )

def handle_elements(path, element):
	
	"""
	Streaming of the xml file
	1. Run thorugh each xml entry, reading as two ordered dicts (path and element)
	2. If it exists, add the 'path' id key (masters id) to the element dict
	3. If it exists, change the 'title' element key to release-title
		(there are 2x title keys in the data - release and video)
	4. Add to relevant mongo db collection
	5. Logging (ids written to file + console counter)
	TODO
	- Fix release-title to be release_title
	"""
	
	# ---- Add id attribute of streamed entry to element dict
	# ---- Do some logging
	
	if 'id' in path[1][1].keys():
		element['item_id'] = path[1][1]['id']
		with open(ids_file,'a') as outfile:
			outfile.write(element['item_id'] + '\n')
	
	# ---- Change the 'id' key of an artist element to 'artist_id'
	# ONLY if artist is in the elements (rather than being the actual artists file)

	if 'artists' in element.keys():
		if type(element['artists']['artist']) is list:
			for artist_item in element['artists']['artist']:
				artist_item['artist_id'] = artist_item.pop('id')
		else:
			element['artists']['artist']['artist_id'] = element['artists']['artist'].pop('id')
	
	# ---- TODO artists / labels / releases logic
	
	#if 'aliases' in element.keys():
	#	for alias in element['aliases']:
	#		artist_item['artist_id'] = artist_item.pop('id')
	
	# ---- Change 'title' in first level to 'release title'
	# See function description
	
	if 'title' in element.keys():
		element['release-title'] = element.pop('title')
	
	# ---- Add to mongo
	
	coll_id = mongo_collection.insert_one( element )
	
	global counter
	counter+=1
	
	console.write('\r{} processed'.format( counter ))
	console.flush()
	
	return True
	
def main(args):
	"""
	Parse a given xml file with xmltodict and insert entries to a mongo database collection
	TODO: 
	1. PARAMETERIZE!!!
		- Need to change the collection + file based on file names
		- re.search or a pre-defined list (only ever 4 files...?)
	"""
	
	# directory structure is /home/{filetype}s/{filename}.{extension}
	
	global counter, ids_file
	counter = 1
	
	ids_file = re.sub('\.xml','_all_processed_ids\.txt',args.inputfile[0])
	
	# ---- This is hacky!!
	# /home/xmls/discogs_20170901_masters.xml
	
	collection_choice = args.inputfile[0].split('01_')[1].split('.xml')[0]
	
	db_dict = {'host' : 'mongo-discogs', 'port': 27017 , 'db' : 'discogs' , 'coll' : str(collection_choice) }

	global mongo_collection
	mongo_collection, ping_result = mongo_cli(db_dict)
	
	print('mongo connection: ', db_dict)
	print('mongo connection ping result: ', ping_result)
	
	with open(args.inputfile[0],'rb') as infile:
		
		prints('\nParsing ' + str(args.inputfile[0]) + ' with xmltodict - writing to mongo collection: ' + str(db_dict['coll']))
		xmltodict.parse(infile,item_depth=2,process_namespaces=True,item_callback=handle_elements)
		prints('\nWritten to mongo collection: '+str(db_dict['coll']))
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="XML to JSON file converter")	
	parser.add_argument('inputfile',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)