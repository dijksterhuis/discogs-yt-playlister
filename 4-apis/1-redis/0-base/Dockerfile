FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-redis-api" \
      purpose="Get the required data from redis" \
      version="base"
RUN mkdir /logging/
COPY *.py /home/
RUN chmod a+x /home/*.py
COPY reqs.txt /home
WORKDIR /home
RUN apk update ; apk upgrade
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
EXPOSE 80