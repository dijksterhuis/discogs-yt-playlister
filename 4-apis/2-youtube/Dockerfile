FROM python:alpine
LABEL author="michael robeson (Dijksterhuis)" \
      project="discogs playlister" \
      name="discogs-youtube-api" \
      purpose="Get the required data from redis" \
      version="dev"
# ---- Folders
WORKDIR /home
RUN mkdir /logging/
COPY *.py /home/
COPY *.json /home/
COPY reqs.txt /home
COPY docker_entrypoint.sh /home
# ---- DoDoDo
RUN chmod a+x /home/*.py
RUN chmod a+x /home/docker_entrypoint.sh
RUN apk update ; apk upgrade
RUN pip install --upgrade -r reqs.txt
RUN rm /home/reqs.txt
# ---- Docker specific
EXPOSE 80
CMD ['./docker_entrypoint.sh']