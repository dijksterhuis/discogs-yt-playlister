FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-redis-api" \
      purpose="Get the required data from redis" \
      version="dev"
RUN mkdir /logging/
COPY *.py /home/
RUN chmod a+x /home/*.py
RUN apk update
RUN pip install --upgrade flask requests redis werkzeug flask-httpauth flask_restful
WORKDIR /home
EXPOSE 5000