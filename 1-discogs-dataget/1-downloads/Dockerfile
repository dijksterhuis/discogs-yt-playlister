FROM alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-db-dls" \
      purpose="Download the latest discogs db xmls" \
      version="0.0.5"

RUN apk update ; apk upgrade ; apk add --no-cache curl

ADD COPY root /etc/crontabs/root
RUN chmod 0644 /etc/crontabs/root
RUN touch /var/log/cron.log

RUN mkdir /home/downloads ; mkdir /home/old_downloads
COPY download_xmls.sh /home
RUN chmod a+x /home/download_xmls.sh
WORKDIR /home/

CMD ['/bin/ash']