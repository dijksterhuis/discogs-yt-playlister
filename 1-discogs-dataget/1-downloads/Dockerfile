FROM alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-db-dls" \
      purpose="Download the latest discogs db xmls" \
      version="0.0.4"

RUN apk update && apk upgrade && apk add --no-cache curl

RUN mkdir /home/downloads && mkdir /home/old_downloads
#VOLUME ["/home/downloads","/home/old_downloads"]

COPY download_xmls.sh /home
RUN chmod a+x /home/download_xmls.sh

WORKDIR /home