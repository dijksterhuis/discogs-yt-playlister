FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="redis-database-inserts" \
      purpose="Extract required metadata from the json files and insert into redis autocomplete / search db..." \
      version="modularised-0.1"
RUN mkdir /logging/
COPY redis-load*.py /home/
COPY reqs.txt /home
RUN chmod u+x /home/*.py
WORKDIR /home
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt