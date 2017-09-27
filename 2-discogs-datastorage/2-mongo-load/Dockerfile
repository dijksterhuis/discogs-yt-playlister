FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-pymongoimport" \
      purpose="Insert enties from json discogs files into mongodb" \
      version="0.0.3"

RUN mkdir /home/jsons

COPY import_jsons.py /home
RUN chmod u+x /home/import_jsons.py

RUN pip install --upgrade pymongo argparse
WORKDIR /home
