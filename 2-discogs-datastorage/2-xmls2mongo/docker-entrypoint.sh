#!/bin/ash
find /home/xmls -name \*.xml | xargs -r0 python /home/mongo_ETL.py --indexing --verbose