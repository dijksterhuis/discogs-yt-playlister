FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="dev"
RUN mkdir /logging/
<<<<<<< HEAD
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
#CMD ["/app/main.py"]
=======
RUN mkdir /home/site/
RUN mkdir /home/data/
COPY flask-site/ /home/site/
WORKDIR /home
RUN apk update ; apk add wget unzip
#RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O /home/ngrok-stable-linux-amd64.zip
#RUN unzip ./ngrok-stable-linux-amd64.zip
COPY reqs.txt /home/
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["/home/site/main.py"]
>>>>>>> parent of 426ce63... nginx, uswgi serving / message flashing / clean up
