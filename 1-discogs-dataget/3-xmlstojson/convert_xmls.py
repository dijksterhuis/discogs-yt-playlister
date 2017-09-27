#!/usr/local/bin/python

import xmltodict, json, argparse, re

def prints(string):
	"""
	Print the string if verbosity (argparse arg) is true
	"""
	if verbose_bool is True:
		print(string)

def main(args):
	"""
	Parse a given xml file with xmltodict
	Write output to a 'prettified' json file
	N.B. Output path generated from input path
	"""
	try:
		with open(args.inputfile[0],'rb') as infile:
			prints('\nParsing ' + str(args.inputfile[0]) + ' with xmltodict \n')
			output = xmltodict.parse(infile,item_depth=0,process_namespaces=True)
			prints('\nfilelength: ' +str(len(output))+'\n')
	except IOError:
		prints("Error: can't find file or read data")
		#os.EX_NOINPUT
		exit(66)
	except MemoryError:
		prints("Memory Error!")
		exit()
	except:
		prints("An unknown error occured, check traceback")
		exit()
	
	# directory structure is /home/{filetype}s/{filename}.{extension}
	# so substituting "xml" with "json" creates output path
	
	outputfile = re.sub('xml','json',args.inputfile[0])
	prints('\nWriting to ' + outputfile + '\n')
	
	try:
		with open(outputfile,'w') as outfile:
			prints('Writing json to ' + outputfile)
			outfile.write( json.dumps( output, sort_keys=True, indent=4 ) )	
			prints('Written json to ' + outputfile)

	except IOError:
		prints("Error: can't find file or read data")
		#os.EX_NOINPUT
		exit(66)
	except MemoryError:
		prints("Memory Error!")
		exit()
	except:
		prints("An unknown error occured, check traceback")
		exit()

		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="XML to JSON file converter")	
	parser.add_argument('inputfile',type=str,nargs=1)
	parser.add_argument('--verbose',action='store_true')
	args = parser.parse_args()
	global verbose_bool
	verbose_bool = args.verbose
	main(args)