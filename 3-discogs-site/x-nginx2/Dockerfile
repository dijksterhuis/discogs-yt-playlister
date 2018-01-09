FROM debian:stretch
# https://realpython.com/blog/python/kickstarting-flask-on-ubuntu-setup-and-deployment/
RUN apt-get update
RUN apt-get install -y python python-pip python-virtualenv nginx gunicorn supervisor python-certbot-nginx
RUN mkdir -p /app
COPY reqs.txt /tmp
RUN pip install --upgrade -r /tmp/reqs.txt
COPY flask-site/ /app
RUN rm /etc/nginx/sites-enabled/default
RUN touch /etc/nginx/sites-available/discogs-yt-playlister
RUN ln -s /etc/nginx/sites-available/discogs-yt-playlister /etc/nginx/sites-enabled/discogs-yt-playlister
COPY discogs-yt-playlister /etc/nginx/sites-enabled/discogs-yt-playlister/
COPY discogs-yt-playlister.conf /etc/supervisor/conf.d/
COPY start.sh /
WORKDIR /app
CMD ['start.sh']