FROM alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-nginx-proxy" \
      purpose="Discogs yt playlister nginx proxy" \
      version="dev"
# https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#putting-behind-a-full-webserver
# https://github.com/dockerfile/nginx/blob/master/Dockerfile
RUN mkdir -p /logging/
RUN apk update ; apk upgrade ; apk add nginx
COPY nginx.conf /etc/nginx
RUN mkdir -p /data
VOLUME ["/etc/nginx/sites-enabled", "/etc/nginx/certs", "/etc/nginx/conf.d", "/var/log/nginx", "/var/www/html"]
EXPOSE 70
EXPOSE 80
EXPOSE 443
EXPOSE 3031
#ENTRYPOINT ['nginx']