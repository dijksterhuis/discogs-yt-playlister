FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="dev"
RUN mkdir /logging/
COPY flask-site/ /app
WORKDIR /app
COPY reqs.txt /app/
RUN pip install --upgrade -r reqs.txt
RUN rm /app/reqs.txt
#RUN apt-get update ; apt-get install -y python-certbot-nginx
EXPOSE 80
#EXPOSE 443
#ENV LISTEN_PORT 443
#RUN export OAUTHLIB_INSECURE_TRANSPORT=1
#ENTRYPOINT ['/bin/bash']
#CMD ['certbot','--nginx']
CMD ["/home/main.py"]