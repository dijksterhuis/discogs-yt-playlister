FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="redis-database-inserts" \
      purpose="Extract required metadata from the json files and insert into redis autocomplete / search db..." \
      version="modularised-0.1"
RUN mkdir /logging/
COPY redis-load*.py /home/
RUN chmod u+x /home/*.py
RUN pip install --upgrade reqs.txt
WORKDIR /home