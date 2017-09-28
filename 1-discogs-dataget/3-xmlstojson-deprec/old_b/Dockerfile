FROM python

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      purpose="Run convert_xmls.py to convert discogs xml data to jsons strings then load into a mpongo database" \
      version="0.0.1"

RUN pip install --upgrade xmltodict pymongo argparse

# Volume: discogs-db-xmls
RUN mkdir /home/xmls

# Volume: discogs-db-jsons
RUN mkdir /home/jsons

# Old xml to dict
COPY convert_xmls_003.py /home
RUN chmod a+x /home/convert_xmls_003.py

# Old xml to dict
COPY convert_and_load.sh /home
RUN chmod a+x /home/convert_and_load.sh



# discogs-xml2db version

# https://github.com/philipmat/discogs-xml2db
#RUN git clone https://github.com/philipmat/discogs-xml2db.git /discogs-xml2db

#COPY convert_to_json.sh /discogs-xml2db
#RUN chmod a+x /discogs-xml2db/convert_to_json.sh

WORKDIR /home/
