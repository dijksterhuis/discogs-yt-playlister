FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="dev"
RUN mkdir /logging/
RUN mkdir /home/site/
RUN mkdir /home/data/
COPY flask-site/ /home/site/
WORKDIR /home
RUN apk update ; apk add wget unzip
COPY reqs.txt /home/
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
# https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-flask
EXPOSE 80
EXPOSE 3031
EXPOSE 9191
ENTRYPOINT ["uwsgi"]
CMD ["--socket 127.0.0.1:3031 --wsgi-file /home/site/main.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191"]