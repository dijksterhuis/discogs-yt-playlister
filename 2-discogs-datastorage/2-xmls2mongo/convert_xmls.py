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
	mongo = MongoClient(db_dict['host'],db_dict['port'])
	db = mongo[db_dict['db']]
	db.drop_collection(db_dict['coll'])
	collection = db[db_dict['coll']]
	return collection

def handle_elements(path, element):
	#try:
	if path[1][1] is not None:
		element['id'] = path[1][1]['id']
	coll_id = mongo_collection.insert_one( element )
	#with open(outputfile,'a') as outfile:
	#	outfile.write(json.dumps( element, sort_keys=True, indent=4 ))
	with open(ids_file,'a') as outfile:
		outfile.write(element['id'] + '\n')
	global counter
	counter+=1
	console.write('\r{} processed'.format( counter ))
	return True
	
	#except IOError:
	#	io_err()
	#except MemoryError:
	#	mem_err()
	#except:
	#	misc_err()
	
def main(args):
	"""
	Parse a given xml file with xmltodict
	Write output to a 'prettified' json file
	N.B. Output path generated from input path
	"""
	
	# directory structure is /home/{filetype}s/{filename}.{extension}
	# so substituting "xml" with "json" creates output path
	global counter, ids_file #, outputfile
	counter = 1
	ids_file = re.sub('\.xml','_all_processed_ids\.txt',args.inputfile[0])
	#, outputfile = 1 , re.sub('xml','json',args.inputfile[0])
	
	db_dict = {'host' : 'discogs-mongo', 'port': 27017 , 'db' : 'discogs' , 'coll' : 'masters'}

	global mongo_collection
	mongo_collection = mongo_cli(db_dict)
	
	#try:
	with open(args.inputfile[0],'rb') as infile:
		prints('\nParsing ' + str(args.inputfile[0]) + ' with xmltodict - writing to mongo collection: ' + str(db_dict['coll']))
		xmltodict.parse(infile,item_depth=2,process_namespaces=True,item_callback=handle_elements)
		prints('\nWritten to mongo collection: '+str(db_dict['coll']))
		#prints('\nFinished parsing and writing to '+outputfile)
	#except IOError:
	#	io_err()
	#except MemoryError:
	#	mem_err()
	#except:
	#	misc_err()
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="XML to JSON file converter")	
	parser.add_argument('inputfile',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)