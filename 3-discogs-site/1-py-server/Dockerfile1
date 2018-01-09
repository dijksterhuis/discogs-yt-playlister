FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-server" \
      purpose="Discogs yt playlister flask webserver" \
      version="dev"
RUN mkdir /logging/
RUN mkdir /home/site/
RUN mkdir /home/data/
COPY flask-site/ /home/site/
WORKDIR /home
COPY reqs.txt /home/
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["/home/site/main.py"]
