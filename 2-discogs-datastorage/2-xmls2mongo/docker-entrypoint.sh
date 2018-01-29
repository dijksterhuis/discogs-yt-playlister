#!/bin/ash
find /home/xmls -name \*.xml -print -exec python mongo_ETL.py --indexing --verbose {} \;