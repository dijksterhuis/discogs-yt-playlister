FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-pymongoimport" \
      purpose="Insert enties from json discogs files into mongodb" \
      version="0.0.3"

RUN mkdir /home/xmls

COPY *.py /home/
RUN chmod a+x /home/*.py

RUN pip install --upgrade pymongo argparse xmltodict
WORKDIR /home
