#!/usr/local/bin/python3

"""
Is this going to be in a flask app?
Or a go app?
Or Java backend?
"""

import redis,requests

r_conn = redis.Redis(host='localhost',port='6379')

year_choices = ['2000','2001','2002','2003']
genre_choices = ['Rock','Electronic']
style_choices = ['Techno','Ambient']

year_selector = ['year:' + str(i) for i in year_choices]
genre_selector = ['genre:' + str(i) for i in genre_choices]
style_selector = ['style:' + str(i) for i in style_choices]

# redis pipeline was WAY faster in testing...

pipe = r_conn.pipeline()
videos_pipe = r_conn.sunion( [ 'video:' + i.decode('ascii') for i in iter( \
										r_conn.sunion(year_selector) \
										& r_conn.sunion(genre_selector) \
										& r_conn.sunion(style_selector)) ] )
pipe.execute()

for video in videos_pipe:
	data = requests.get(url=video.decode('ascii'))
	print(video.decode('ascii'))
	print(data)