FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-pymongoimport" \
      purpose="Insert enties from json discogs files into mongodb" \
      version="0.9.0"

WORKDIR /home
RUN mkdir /home/xmls

# Add python files to /home
COPY *.py /home/
RUN chmod a+x /home/*.py

# install required python libraries
RUN pip install --upgrade reqs.txt

# Execution command
# TODO: Create an entrypoint so can test different ETL scripts 
# TODO: Docker build-then-run script so don't have to keep changing this file - how to do version number? Jenkins?
CMD ['cd','/home',';','find','/home/xmls','-name','\*.xml','|','xargs','-r0','./mongo_ETL.py']