FROM dijksterhuis/discogs-flask-redis-api:base
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-flask-redis-api" \
      purpose="Get the required data from redis" \
      version="form-metadata"
COPY *.py /home/
ENTRYPOINT ["python"]
CMD ["/home/redis_flask_api.py"]