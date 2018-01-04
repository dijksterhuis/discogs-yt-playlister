FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Extract required metadata from the masters json file..." \
      version="dev"
RUN mkdir /logging/
RUN mkdir /home/site/
RUN mkdir /home/data/
#COPY flask-site/ /home/site/
#RUN chmod u+x /home/*.py
RUN apk update ; apk add wget unzip
#RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O /home/ngrok-stable-linux-amd64.zip
#RUN unzip ./ngrok-stable-linux-amd64.zip
RUN pip install --upgrade flask requests joblib redis pymongo werkzeug google-api-python-client httplib2
WORKDIR /home