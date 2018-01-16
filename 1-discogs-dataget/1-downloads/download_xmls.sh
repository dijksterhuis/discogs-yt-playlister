#!/bin/ash
# https://www.dwheeler.com/essays/filenames-in-shell.html

IFS="$(printf '\n\t')"
	# or:
	IFS="`printf '\n\t'`"
	# Widely supported, POSIX added http://austingroupbugs.net/view.php?id=249
	IFS=$'\n\t'

##### 1
# - Variable declarations - working path, current dates
year=`date +"%Y"`
yearmonth=`date +"%Y%m"`
discogsurlprefix="http://discogs-data.s3-us-west-2.amazonaws.com/data/""$year""/"

##### 2
# - Copy yesterday's data to old_data dir (archive) and remove from downloads dir

dl=/home/downloads/
olddl=/home/old_downloads/

echo "Moving existing xml files to backup dir"
find $dl -name /home\*.xml -print -exec mv {} $olddl \;

##### 3
# - Curl and gzip decompress each new file
# - Pipe gzip output to stdout then to file in case of unexpected EOF
# curl fileurl | gzip -dc > test.xml


md5file="discogs_"$yearmonth"01_CHECKSUM.txt"
curl $discogsurlprefix$md5file -o $dl$md5file

for type in artists labels masters releases; \
    do \
        infile="discogs_"$yearmonth"01_"$type".xml.gz"
        outfile=$dl"discogs_"$yearmonth"01_"$type".xml"
        echo "Curling file: " $infile ;
        curl $discogsurlprefix$infile -o $dl$infile
     done

cd $dl

md5sum -c $md5file

echo "Gzip decompressing files"
gzip -d *

cd /home