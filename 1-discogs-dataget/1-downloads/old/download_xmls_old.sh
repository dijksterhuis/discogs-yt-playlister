#!/bin/bash

# https://www.dwheeler.com/essays/filenames-in-shell.html

IFS="$(printf '\n\t')"
	# or:
	IFS="`printf '\n\t'`"
	# Widely supported, POSIX added http://austingroupbugs.net/view.php?id=249
	IFS=$'\n\t'

# Variable declarations - working path, current dates
year=`date +"%Y"`
yearmonth=`date +"%Y%m"`
discogsurlprefix="http://discogs-data.s3-us-west-2.amazonaws.com/data/""$year""/"

# Copy last month's data to old_data directory

echo "Copy old files to backup"
for file in $(find . -maxdepth 1 -name '*.xml') ;\
	do \
	echo "Copying old xml file: " "$file" ; \
	echo "To: " ./"old_data"/"$file" ; \
	echo "" ; \
	cp "$file" ./"old_data"/"$file" ; \
	done

# Get each new file and gunzip it in this directory

for type in artists labels masters releases ; \
	do \
        infile="discogs_""$yearmonth""01_""$type"".xml.gz"
        outfile="$yearmonth""$type"".xml.gz"
	    echo "Curling file: ""$infile"" to ""$outfile" ;
	    curl -o ./"$outfile" "$discogsurlprefix""$infile" ; \
	done

# Remove old data from current directory

for file in $(find . -maxdepth 1 -name "$yearmonth"'*.xml') ; \
        do \
        echo "Removing: " "$file"
        rm "$file" ; \
        done