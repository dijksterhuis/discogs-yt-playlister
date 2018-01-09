FROM tiangolo/uwsgi-nginx-flask:python3.6
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="dev"
RUN mkdir /logging/
COPY flask-site/ /app
WORKDIR /home
COPY reqs.txt /home/
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
RUN apt-get install -y python-certbot-nginx
RUN certbot --nginx
EXPOSE 80
EXPOSE 443
ENV LISTEN_PORT 443
RUN export OAUTHLIB_INSECURE_TRANSPORT=1
