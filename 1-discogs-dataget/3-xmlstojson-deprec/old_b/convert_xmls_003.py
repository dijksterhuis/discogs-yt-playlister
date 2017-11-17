#!/usr/local/bin/python

import xmltodict, json, argparse, pymongo
import xml.etree.cElementTree as etree
from sys import stdout as console
from pymongo import MongoClient as mc


def prints(string,verbose_bool):
	if verbose_bool is True:
		print(string)

def handle_elements(_, element):
	element = json.loads(json.dumps(element))
	#if 'id' in element[ collection_str[ 0:len(collection_str)-1 ] ].keys():
	#collection.create_index([('id', pymongo.ASCENDING)],unique=True)
	collection_id = collection.insert_one(element)
	global counter
	counter +=1
	console.write('%s\r' % str(collection_str)+' collection :: '+str(collection_id.inserted_id)+' added :: '+str(counter)+' processed')
	console.flush()
	return True

def main(args):

	global collection_str
	global collection
	global counter
	counter = 0
	
	mongo_client = mc('discogs-jsons',27017)
	db = mongo_client['discogs-jsons']

	files = ['artists','labels','masters','releases']
	collection_str = [ i for i in files if i in args.inputfile[0]]

	if len(collection_str) == 0:
		print('The input file is not artists, labels, masters or releases')
		print('Exiting')
		exit()
	else:
		collection_str = collection_str[0]
		
	db.drop_collection(collection_str)
	collection = db[collection_str]
	
	with open(args.inputfile[0],'rb') as infile:
		prints(infile,args.verbose)
		prints('Parsing',args.verbose)
		# streaming version!
		o = xmltodict.parse(infile,item_depth=1,item_callback=handle_elements,process_namespaces=True)
		

	print('Added data from ' + args.inputfile[0] + ' to ' + collection_str + ' collection')

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="XML to JSON file converter")	
        parser.add_argument('inputfile',type=str,nargs=1)
        #parser.add_argument('collection',type=str,nargs=1)
        parser.add_argument('--verbose',action='store_true')
        args = parser.parse_args()	
        main(args)