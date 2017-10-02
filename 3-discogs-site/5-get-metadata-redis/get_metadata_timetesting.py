#!/usr/local/bin/python3

"""
Is this going to be in a flask app?
Or a go app?
Or Java backend?
"""

import redis
from datetime import datetime as dt
from sys import stdout as console

starttime = dt.now()

r_conn = redis.Redis(host='localhost',port='6379')

year_choices = ['2000','2001','2002','2003']
genre_choices = ['Rock','Electronic']
style_choices = ['Techno','Ambient']

year_selector = ['year:' + str(i) for i in year_choices]
genre_selector = ['genre:' + str(i) for i in genre_choices]
style_selector = ['style:' + str(i) for i in style_choices]

timings = [dt.now()] # 0
year_union = r_conn.sunion(year_selector)
timings.append(dt.now()) # 1
genre_union = r_conn.sunion(genre_selector)
timings.append(dt.now()) # 2
style_union = r_conn.sunion(style_selector)
timings.append(dt.now()) # 3
intersection_output_1 = style_union & genre_union & year_union
timings.append(dt.now()) # 4
videos = r_conn.sunion( [ 'video:' + i.decode('ascii') for i in iter(intersection_output_1) ] )
timings.append(dt.now()) # 5

print('\n Query 1 - number of videos returned: ' + str(len(videos)))
print('Query 1 - timings')
for idx, itemtime in enumerate(timings):
	total_elapsed = itemtime - starttime
	if idx ==0:
		prev_elapsed = itemtime - starttime
	else:
		prev_elapsed = itemtime - timings[idx-1]
	console.write("\n idx {} total {} since prev {} -- ".format(idx, total_elapsed, prev_elapsed))

timings = [dt.now()] # 0
insersection_output_2 = r_conn.sunion(year_selector) & r_conn.sunion(genre_selector) & r_conn.sunion(style_selector)
timings.append(dt.now()) # 1
videos = r_conn.sunion( [ 'video:' + i.decode('ascii') for i in iter(insersection_output_2) ] )
timings.append(dt.now()) # 2

print('\n\nQuery 2 - number of videos returned: ' + str(len(videos)))
print('Query 2 - timings')
for idx, itemtime in enumerate(timings):
	total_elapsed = itemtime - starttime
	if idx ==0:
		prev_elapsed = itemtime - starttime
	else:
		prev_elapsed = itemtime - timings[idx-1]
	console.write("\n idx {} total {} since prev {} -- ".format(idx, total_elapsed, prev_elapsed))


starttime = dt.now()
pipe = r_conn.pipeline()

videos_pipe = r_conn.sunion( [ 'video:' + i.decode('ascii') for i in iter( \
										r_conn.sunion(year_selector) \
										& r_conn.sunion(genre_selector) \
										& r_conn.sunion(style_selector)) ] )

pipe.execute()
print('\n\nPipeline 1 - number of videos returned: ' + str(len(videos_pipe)))
print('Pipeline 1 - timings')
print(dt.now() - starttime)

#Or_filter_masters = set.union(*[r.sunion(year_selection) , r.sunion(genre_selection) , r.sunion(style_selection)])