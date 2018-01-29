#!/bin/ash
find /home/xmls -name \*.xml -print -exec /home/mongo_ETL.py {} --indexing --verbose {} \;