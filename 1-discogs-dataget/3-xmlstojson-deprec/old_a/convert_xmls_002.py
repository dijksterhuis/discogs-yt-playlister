#!/usr/local/bin/python

import xmltodict, json, argparse
import xml.etree.cElementTree as etree
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
		collection_str = collection[0]
		
	db.drop_collection(collection_str)
	collection = db[collection_str]
	print(collection)
	#prints(collection_id.inserted_ids)
	
	with open(args.inputfile[0],'rb') as infile:

		prints(infile,args.verbose)
		prints('Parsing',args.verbose)
		print('parsing')
		tree = etree.iterparse(infile,events=('start',))
		print(tree)
		tree_to_dict = {elem.tag:elem.text if elem.text is not None else elem.attrib for event,elem in tree if elem.tag != collection_str}
		print(tree_to_dict)
		for event, elem in tree:
			print('element',str(elem.tag),'text',str(elem.text),'attrib',str(elem.attrib))
		
		#o = xmltodict.parse(infile,item_depth=1,item_callback=handle_elements)
		#o = xmltodict.parse(infile)
	#prints(o)

	print('Added data from ' + args.inputfile[0] + ' to ' + collection_str + ' collection')

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="XML to JSON file converter")	
        parser.add_argument('inputfile',type=str,nargs=1)
        #parser.add_argument('collection',type=str,nargs=1)
        parser.add_argument('--verbose',action='store_true')
        args = parser.parse_args()	
        main(args)