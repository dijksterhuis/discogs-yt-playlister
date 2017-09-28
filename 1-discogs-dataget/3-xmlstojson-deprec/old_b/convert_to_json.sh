#!/bin/bash
#yearmonth=`date +"%Y%m"`"01"
#./discogsparser.py -d "$yearmonth" -n 1000 -o mongo -p "file://jsons/"
# "mongodb://localhost/discogs-jsons"
#find /home/xmls -name \*.xml -print -exec python3 discogsparser.py {} -n 1000 -o json > "/home/jsons/"$(basename {} .xml)'.json' \;

# https://www.dwheeler.com/essays/filenames-in-shell.html

IFS="$(printf '\n\t')"
	# or:
	IFS="`printf '\n\t'`"
	# Widely supported, POSIX added http://austingroupbugs.net/view.php?id=249
	IFS=$'\n\t'

xmls=/home/xmls/
jsons=/home/jsons/
yearmonth=`date +"%Y%m"`

for file in artists labels masters releases ; \
    do \
        infile=$xmls"discogs_"$yearmonth"01_"$file".xml" 
        outfile=$jsons"discogs_"$yearmonth"01_"$file".json" 
        echo "parsing " $infile " to " $outfile ; 
        python3 discogsparser.py "$infile" -n 1000 -o json > $outfile ; \
    done