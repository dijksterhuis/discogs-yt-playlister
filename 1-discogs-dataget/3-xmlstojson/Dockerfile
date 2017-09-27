FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-xml2json" \
      purpose="Run convert_xmls.py to convert discogs xml data to jsons strings" \
      version="0.0.4"

RUN pip install --upgrade xmltodict argparse

# Volume: discogs-db-xmls
RUN mkdir /home/xmls

# Volume: discogs-db-jsons
RUN mkdir /home/jsons

# python script
COPY convert_xmls.py /home
RUN chmod a+x /home/convert_xmls.py

WORKDIR /home/
