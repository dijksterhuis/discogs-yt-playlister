#!/bin/bash
find /home/jsons -name \*.xml -exec /home/convert_xmls.py {} \;
