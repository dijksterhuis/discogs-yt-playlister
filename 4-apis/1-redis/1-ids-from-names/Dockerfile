FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-redis-api" \
      purpose="Get the required data from redis" \
      version="ids-from-names"
RUN mkdir /logging/
COPY *.py /home/
RUN chmod a+x /home/*.py
RUN apk update ; apk upgrade
RUN pip install --upgrade -r reqs.txt
WORKDIR /home
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["/home/redis_flask_api.py"]