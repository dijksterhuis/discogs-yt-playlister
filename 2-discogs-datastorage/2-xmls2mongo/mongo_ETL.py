#!/usr/bin/python

import xmltodict, json, argparse, re, os
from sys import stdout as console
import pymongo

"""
TODO
1. Data files don't necessarily upload on 01 of month.
	input: /home/xmls/discogs_20170901_masters.xml
	expected output: masters
	line affected: collection_choice = infile.split('01_')[1].split('.xml')[0]
	solution: Need to do some form of regex that matches the numbers from 20170101_ and splits
2. Is all the relases data covered?
3. If the releases file, only keep certain elements to save memory usage (mongo eats it up on my 16GB box)
(This needs checking!)
	- release id
	- release title
	- main_release
	- label id
	- release date
	- companies - id, entity type / desc ?
	- extra artists ?
	- artists ?
	- country ?
"""

def s(string):
	"""
	I like saving space across my screen
	"""
	return str(string)

def print_verbose(string):
	"""
	Print the string if verbosity (argparse arg) is true
	"""
	if verbose_bool is True:
		print(string)

def io_err():
	print_verbose("Error: can't find file or read data")
	#os.EX_NOINPUT
	exit(66)
def mem_err():
	print_verbose("Memory Error!")
	exit()
def misc_err():
	print_verbose("An unknown error occured, check traceback")
	exit()

def mongo_cli(db_dict):
	"""
	Set up a connection and default index for mongo db/coll using input dictionary
	Also return the result of a ping command sent to the database
	input - db_dict = {'host' : 'mongo-discogs', 'port': 27017 , 'db' : 'discogs' , 'coll' : collection }
	outputs - (collection , ping result)
	"""
	
	mongo = pymongo.MongoClient(db_dict['host'],db_dict['port'])
	db = mongo[db_dict['db']]
	collection = db[db_dict['coll']]
	if mongo_indexing == True:
		db.profiles.create_index([(collection_choice+'_id',pymongo.ASCENDING )],name=collection_choice+'_id',unique=True)
		indexes = sorted(list(db.profiles.index_information()))
	else:
		indexes = "No Indexes created"
	ping_result = mongo[db_dict['db']].command('ping')
	return (collection , indexes , ping_result )

def recursive_elements(element,keys_tuple,new_key,start_counter=0):
	"""
	Check element for specified keys
	------------------------------------------------------------------
	- If a key does not exist:
		- drop down into element level through recursion
		- check if it exists on later levels
	- If a key does exist:
		- Pop the value into the element dict under new_key
	"""
	
	# -- if current element is a list, then we need to iterate over it and perform recursion again
	# the try except clause was to skip past an annoying TypeError when the recusion resets
	# videos have a title key, but the release title is also called title key
	# attempting to pop the release title key in the same way as here results in a TypeError
	# FIX: this was fixed by processing the release_title field first...
	
	if element is None:
		pass
	
	elif type(element) is list:
			for list_item in element:
				for idx, key in enumerate(keys_tuple[start_counter:]):
					if key in list_item.keys():
						for b in recursive_elements(list_item,keys_tuple,new_key,start_counter):
							yield True
					else:
						yield False
						
	# -- if at the last key address in keys_tuple, then pop the relevant dictionary element and return a True value
	
	elif len(keys_tuple[start_counter:]) == 1:
		old_key = keys_tuple[start_counter:][0]
		if type(element) is not list and old_key in element.keys():
			element[new_key] = element.pop(old_key)
			yield True
		else:
			yield False

	# -- else we need to recurse down further to find the relevant key name to swap
	# break fixes an AttributeError - 'title' name once again...!

	elif len(keys_tuple[start_counter:]) > 1:
		key = keys_tuple[start_counter:][0]
		if key in element.keys():
			start_counter+=1
			for b in recursive_elements(element[key],keys_tuple,new_key,start_counter):
				yield True
		else:
			yield False
	
	else:
		yield False

def handle_elements(path, element):
	
	"""
	Streaming of the xml file
	1. Run thorugh each xml entry, reading as two ordered dicts (path and element)
	2. If it exists, add the 'path' id key (e.g. masters id) to the element dict
	3. Drop keys that aren't required
	4a. Recursively parse the nested dictionary and flatten it
	4b. Change the nested key names to flattened key names using the 'changes' tuple array below
	5. Add to relevant mongo db collection
	6. Logging (ids written to file + console counter)
	"""
	
	if type(element) is None or element is None:
		print('\nNo data in xml element!!\n')
	
	# ---- Create YEAR, MONTH & DATE entries for release date (releases only)
	if 'released' in element.keys()
		element['released-year'], element['released-month'], element['released-dotm'] = element['released'].split('-')
		element['released-date'] = element.pop('released')
	
	elif None not in path[1]:
		# ---- Add id attribute of streamed entry to element dict
		if 'id' in path[1][1].keys():
			element[ s(collection_choice) + '_id' ] = int(path[1][1]['id'])
	elif 'id' in element.keys():
		element[ s(collection_choice) + '_id' ] = int(element.pop('id'))
	
	# remove non-useful elements (if they exist)
	# e.g. get rid of images and tracks data, we don't need it
	
	keys_to_drop = [ \
					'images' \
					,'tracks' \
					,'identifiers' \
					,'formats' \
					,'namevariations' \
					,'tracklist' \
					,'companies' \
					,'aliases' \
					,'urls' \
					,'sublabels' \
					,'notes' \
					,'profile' \
				]
	
	for key in keys_to_drop:
		if key in element.keys():
			element.pop(key)
	
	# ---- Change titles of elements to more useful names for redis load recursive searching
	# please note that any elements from keys_to_drop will not be looked for in the recursive searching
	# (the keys are kept in the changes array for reference purposes / should the keys_to_drop need to change)
	changes = [ \
				(('title',) , 'release_title') \
				, (('urls',) , 'artist_urls')
				, (('profile',) , 'artist_profile') \
				, (('name',) , 'artist_name') \
				, (('realname',) , 'artist_realname') \
				, (('members', 'id' ) , 'member_id') \
				, (('members', 'name' ) , 'member_name') \
				, (('aliases', 'name') , 'alias_name') \
				, (('artist_urls', 'url') , 'artist_url') \
				, (('sublabels', 'label') , 'sublabel_name') \
				, (('artists', 'artist','id' ) , 'artist_id') \
				, (('artists', 'artist', 'name' ) , 'artist_name') \
				, (('artists', 'artist', 'tracks' ) , 'artist_tracks') \
				, (('artists', 'artist', 'join' ) , 'artist_join') \
				, (('artists', 'artist', 'role' ) , 'artist_role') \
				, (('artists', 'artist', 'anv' ) , 'artist_anv') \
				, (('extraartists', 'artist','id' ) , 'extra_artist_id') \
				, (('extraartists', 'artist', 'name' ) , 'extra_artist_name') \
				, (('extraartists', 'artist', 'tracks' ) , 'extra_artist_tracks') \
				, (('extraartists', 'artist', 'join' ) , 'extra_artist_join') \
				, (('extraartists', 'artist', 'role' ) , 'extra_artist_role') \
				, (('extraartists', 'artist', 'anv' ) , 'extra_artist_anv') \
				, (('labels', 'label', 'id' ) , 'label_id') \
				, (('videos', 'video', 'title' ) , 'video_title') \
				, (('videos', 'video', 'description' ) , 'video_desc') \
				, (('videos', 'video', '@duration' ) , 'video_duration') \
				, (('videos', 'video', '@src' ) , 'video_url') \
				, (('videos', 'video', '@embed' ) , 'video_embedded') \
				, (('labels', 'label', '@catno' ) , 'label_catno') \
				, (('labels', 'label', '@id' ) , 'label_id') \
				, (('labels', 'label', '@name' ) , 'label_name') \
				, (('namevariations', 'name') , 'namevar_name') \
				, (('companies', 'company', 'id' ) , 'company_id') \
				, (('companies', 'company', 'name' ) , 'company_name') \
				, (('images', 'image', '@uri' ) , 'image_url') \
				, (('images', 'image', '@type' ) , 'image_type') \
				, (('images', 'image', '@width' ) , 'image_width') \
				, (('images', 'image', '@height' ) , 'image_height') \
				, (('images', 'image', '@uri150' ) , 'image_url_150') \
				, (('tracks', 'track', 'title' ) , 'track_title') \
				, (('tracks', 'track', 'duration' ) , 'track_duration') \
				, (('tracklist', 'track', 'position' ) , 'tracklist_position') \
				, (('tracklist', 'track', 'title' ) , 'tracklist_title') \
				, (('tracklist', 'track', 'duration' ) , 'tracklist_duration') \
				, (('identifiers', 'identifier', '@description' ) , 'identifier_desc') \
				, (('identifiers', 'identifier', '@type' ) , 'identifier_type') \
				, (('identifiers', 'identifier', '@value' ) , 'identifier_value') \
				, (('formats', 'format', '@name' ) , 'format_name') \
				, (('formats', 'format', '@qt' ) , 'format_quantity') \
				, (('formats', 'format', '@text' ) , 'format_text') \
				, (('formats', 'format', 'descriptions', 'description' ) , 'format_descriptors') \
			]
			
	correct_changes_per_iter, skipped_keys_per_iter = 0,0
	for idx,pair in enumerate(changes):
		key_address, key_change_value = pair
		if key_address[0] in keys_to_drop:
			pass
		elif key_address[0] not in element.keys():
			pass
		else:
			for k in recursive_elements(element,key_address,key_change_value):
				if k is True:
					correct_changes_per_iter += 1
				elif k is False:
					skipped_keys_per_iter += 1
	
	# ---- Add to mongo
	
	global counter, correct_changes, skipped_keys, duplicate_keys
	
	try:
		result = mongo_collection.insert_one( element )
		counter += 1
	except DuplicateKeyError:
		print('errr')
		duplicate_keys += 1
	
	correct_changes += correct_changes_per_iter
	skipped_keys += skipped_keys_per_iter
	
	console.write('\r{} inserted, {} title change, {} key search empty {} skipped insert'.format(counter, correct_changes , skipped_keys , duplicate_keys ))
	console.flush()
	
	return True
	
def main(args):
	"""
	Parse a list of xml files with xmltodict and insert entries to a mongo database collection
	"""
	for infile in args.inputfiles:
		# directory structure is /home/{filetype}s/{filename}.{extension}
	
		global counter, correct_changes, skipped_keys, duplicate_keys, collection_choice, mongo_collection
		counter, correct_changes, skipped_keys, duplicate_keys = 1,0,0,0
	
		# ---- This is hacky! but it works for 01 files currently...
		# from: /home/xmls/discogs_20170901_masters.xml
		# to: masters
	
		collection_choice = infile.split('01_')[1].split('.xml')[0]
	
		db_dict = { \
					'host' : 'mongo-discogs-'+s(collection_choice) \
					, 'port': 27017 \
					, 'db' : 'discogs' \
					, 'coll' : s(collection_choice) \
				}
			
		mongo_collection, indexes, ping_result = mongo_cli(db_dict)
		print('\nmongo conn: ', db_dict,'\nmongo conn ping t/f: ', ping_result,'\nmongo indexes: ', indexes)
		
		with open(infile,'rb') as f_in_xml:
			print_verbose('\nParsing '+s(f_in_xml)+' with xmltodict - writing to mongo collection: '+s(db_dict['coll']))
			xmltodict.parse(infile,item_depth=2,process_namespaces=True,item_callback=handle_elements)
			print_verbose('\nWritten to mongo collection: '+s(db_dict['coll']))
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="XML to JSON file converter")	
	parser.add_argument('inputfiles',type=str,nargs='+',dest='inputfiles',help="Names of discogs xml files to process")
	parser.add_argument('--verbose',action='store_true',help="Print output verbosely")
	parser.add_argument('--indexing',action='store_true',help="Create mongo indexes on concatenation of collection_name & _id")
	args = parser.parse_args()
	
	# Checks on argparse inputs
	if len(args.inputfiles) < 1:
		print("No input files given")
		exit()
	
	# set up initial global variables
	global verbose_bool, mongo_indexing
	verbose_bool,mongo_indexing = args.verbose, args.indexing
	
	# RUNTIME!
	main(args)