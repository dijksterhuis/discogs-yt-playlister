#!/usr/local/bin/python

import xmltodict, json, argparse, re, os, pickle
from sys import stdout as console

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
	
def handle_elements(path, element):
	#try:
	if path[1][1] is not None:
		element['id'] = path[1][1]['id']
	with open(outputfile,'a') as outfile:
		outfile.write(json.dumps( element, sort_keys=True, indent=4 ))
	global counter
	counter+=1
	console.write('\r{} processed '.format(counter))
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
	global counter, outputfile
	counter, outputfile = 1 , re.sub('xml','json',args.inputfile[0])
	
	#try:
	with open(args.inputfile[0],'rb') as infile:
		prints('\nParsing ' + str(args.inputfile[0]) + ' with xmltodict')
		xmltodict.parse(infile,item_depth=2,process_namespaces=True,item_callback=handle_elements)
		prints('\nFinished parsing and writing to '+outputfile)
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