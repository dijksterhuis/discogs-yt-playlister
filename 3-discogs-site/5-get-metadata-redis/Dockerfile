FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="get-metadata-redis" \
      purpose="Get some metadata from the redis db..." \
      version="testing"
COPY *.py /home/
RUN chmod u+x /home/*.py
RUN pip install --upgrade redis
WORKDIR /home