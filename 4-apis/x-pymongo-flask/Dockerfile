FROM python:alpine

LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-mongo-api" \
      purpose="Get the required data from redis" \
      version="test"

RUN mkdir /logging/

COPY *.py /home/
RUN chmod a+x /home/*.py

RUN apk update ; apk add curl nmap
RUN pip install --upgrade flask requests pymongo werkzeug flask-httpauth flask_restful

#EXPOSE 80

WORKDIR /home