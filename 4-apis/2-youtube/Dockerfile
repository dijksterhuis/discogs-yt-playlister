FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-youtube-api" \
      purpose="Get the required data from redis" \
      version="dev"
RUN mkdir /logging/
COPY *.py /home/
COPY *.json /home/
RUN chmod a+x /home/*.py
COPY reqs.txt /home
WORKDIR /home
RUN apk update ; apk upgrade
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
EXPOSE 80
ENTRYPOINT ['python']
CMD ['youtube_api.py']