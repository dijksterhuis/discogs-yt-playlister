FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="masters-metadata-extraction" \
      purpose="Extract required metadata from the masters json file..." \
      version="testing"
RUN mkdir /logging/
RUN mkdir /home/jsons
COPY *.py /home/
RUN chmod u+x /home/*.py
RUN pip install --upgrade argparse redis joblib pymongo
WORKDIR /home