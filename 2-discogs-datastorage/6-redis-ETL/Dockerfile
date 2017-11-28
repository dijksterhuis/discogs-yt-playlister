FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="redis-database-inserts" \
      purpose="Extract required metadata from the json files and insert into redis autocomplete / search db..." \
      version="dev"
RUN mkdir /logging/
RUN mkdir /home/jsons
COPY *.py /home/
RUN chmod u+x /home/*.py
RUN pip install --upgrade argparse redis joblib pymongo
WORKDIR /home