FROM debian:stretch
# https://realpython.com/blog/python/kickstarting-flask-on-ubuntu-setup-and-deployment/

RUN apt-get update
RUN apt-get install -y python python-pip python-virtualenv nginx gunicorn supervisor
RUN mkdir -p /app
COPY reqs.txt /tmp
RUN pip install --upgrade -r /tmp/reqs.txt
COPY flask-site/ /app
RUN rm /etc/nginx/sites-enabled/default
RUN touch /etc/nginx/sites-available/discogs-yt-playlister
RUN ln -s /etc/nginx/sites-available/discogs-yt-playlister /etc/nginx/sites-enabled/discogs-yt-playlister
COPY nginx.conf /etc/nginx/sites-enabled/discogs-yt-playlister
RUN /etc/init.d/nginx start
COPY flask_project.conf /etc/supervisor/conf.d/
RUN supervisorctl reread
RUN supervisorctl update
WORKDIR /app
ENTRYPOINT ['supervisorctl']
CMD ['start','flask_project']