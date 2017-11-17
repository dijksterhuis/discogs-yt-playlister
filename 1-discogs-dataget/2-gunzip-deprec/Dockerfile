FROM alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="downloads" \
      purpose="Download the latest discogs db xmls"

RUN apk update && apk upgrade && apk add --no-cache gunzip

RUN mkdir /home/downloads && mkdir /home/old_downloads
#VOLUME ["/home/downloads","/home/old_downloads"]

COPY download_xmls.sh /home
RUN chmod a+x /home/download_xmls.sh

WORKDIR /home