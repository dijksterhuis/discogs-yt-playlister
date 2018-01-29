FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-pymongoimport" \
      purpose="Insert enties from json discogs files into mongodb" \
      version="0.9.0"
RUN mkdir /home/xmls
# Add python files to /home
COPY *.py /home/
RUN chmod a+x /home/*.py
COPY reqs.txt /home/
# install required python libraries
RUN pip install --upgrade -r /home/reqs.txt
RUN rm /home/reqs.txt
WORKDIR /home
# Execution command
# TODO: Create an entrypoint so can test different ETL scripts 
# TODO: Docker build-then-run script so don't have to keep changing this file - how to do version number? Jenkins?
# CMD ['find','/home/xmls','-name','\*.xml','|','xargs','-r0','python','/home/mongo_ETL.py']
CMD ['bin/ash/']
ENTRYPOINT§ ['find','/home/xmls','-name','\*.xml','|','xargs','-r0','python','/home/mongo_ETL.py','--indexing']