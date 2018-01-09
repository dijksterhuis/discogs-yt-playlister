/etc/init.d/nginx start
certbot --nginx
supervisorctl reread
supervisorctl update
supervisorctl start discogs-yt-playlister