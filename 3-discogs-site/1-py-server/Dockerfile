FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="nginx"
WORKDIR /home
RUN mkdir /logging/ /home/site/ /home/data/
COPY flask-site/ /home/site/
COPY reqs.txt /home/
RUN pip install --upgrade -r reqs.txt ; rm /home/reqs.txt
RUN apk update ; apk add uwsgi-python
EXPOSE 80
EXPOSE 443
#ENTRYPOINT ["python"]
#CMD ["/home/site/main.py"]
ENTRYPOINT ["/bin/ash"]

