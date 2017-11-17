#!/usr/local/bin/python
import json, argparse, pymongo
from sys import stdout as console
from pymongo import MongoClient

def prints(string,verbose_bool):
	if verbose_bool is True:
		print(string)

def main(args):
	
	coll_str = [ i for i in ['artists','labels','masters','releases'] if i in args.inputfile[0]]

	if len(coll_str) == 0:
		print('The input file is not artists, labels, masters or releases\nExiting\n')
		exit()
	else:
		coll_str = coll_str[0]
	
	mongo = MongoClient('discogs-mongo',27017)
	db = mongo['discogs']
	db.drop_collection(coll_str)
	collection = db[coll_str]
	
	with open(args.inputfile[0],'r') as infile:
		jsondata = json.load(infile)[coll_str]
	
	tot_entries = len(jsondata)
	
	for idx, entry in enumerate(jsondata):
		
		coll_id = collection.insert_one( entry )
		console.write('%s \r' % 'Coll: ' + str(coll_str) + ' | ' + str(idx) + ' of ' + str(tot_entries) + ' processed')
		console.flush()

	print('\nAdded data from ' + args.inputfile[0] + ' to the ' + coll_str + ' collection\n')

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="Pymongo JSON importer")
        parser.add_argument('inputfile',type=str,nargs=1)
        parser.add_argument('--verbose',action='store_true')
        args = parser.parse_args()	
        main(args)