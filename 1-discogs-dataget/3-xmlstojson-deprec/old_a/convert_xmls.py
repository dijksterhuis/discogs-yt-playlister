#!/usr/local/bin/python

import xmltodict, json, argparse
from sys import stdout as console
from pymongo import MongoClient as mc

def prints(string,verbose_bool):
	if verbose_bool is True:
		print(string)

def handle_elements(_, element):
	element = json.loads(json.dumps(element))
	print(element)
	collection_id = collection.insert_one(element)
	console.write('%s\r' % str(collection_id.inserted_id) )
	console.flush()
	#print(dict(element))
	return True

def main(args):

	global collection

	mongo_client = mc('discogs-jsons',27017)
	db = mongo_client['discogs-jsons']

	files = ['artists','labels','masters','releases']
	collection = [ i for i in files if i in args.inputfile[0]]

	if len(collection) == 0:
		print('The input file is not artists, labels, masters or releases')
		print('Exiting')
		exit()
	else:
		collection = collection[0]
		
	db.drop_collection(collection)
	collection = db[collection]
	print(collection)
	#prints(collection_id.inserted_ids)
	
	with open(args.inputfile[0],'rb') as infile:

		prints(infile,args.verbose)
		prints('Parsing',args.verbose)
		print('parsing')
		o = xmltodict.parse(infile,item_depth=1,item_callback=handle_elements)
		#o = xmltodict.parse(infile)
	#prints(o)

	print('Added data from ' + args.inputfile[0] + ' to ' + collection + ' collection')

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="XML to JSON file converter")	
        parser.add_argument('inputfile',type=str,nargs=1)
        #parser.add_argument('collection',type=str,nargs=1)
        parser.add_argument('--verbose',action='store_true')
        args = parser.parse_args()	
        main(args)