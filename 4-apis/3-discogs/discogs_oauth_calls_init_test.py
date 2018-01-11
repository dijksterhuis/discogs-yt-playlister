import sys, discogs_client
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import json, os, datetime, time, requests
from random import randint


import json
import sys
import urllib
import urlparse

import oauth2 as oauth


# https://github.com/jesseward/discogs-oauth-example/blob/master/discogs_example.py
# https://www.discogs.com/applications/edit/16092

# - to install discogs_client from github:
# wget/curl etc. https://github.com/discogs/discogs_client.git
# pip install -e discogs_client dir


CONSUMER_KEY = 'JPrYAjenmsVzglNdpuxG'
CONSUMER_SECRET = 'ZiXHVuuuaitcIvsCxuUaOkFFTdmaeTjx'
REQUEST_TOKEN_URL =	'https://api.discogs.com/oauth/request_token'
AUTHORIZE_URL = 'https://www.discogs.com/oauth/authorize'
ACCESS_TOKEN_URL= 'https://api.discogs.com/oauth/access_token'
USER_AGENT = 'discogs-yt-playlister/1.0'
DISCOGS_CLIENT = discogs_client.Client(USER_AGENT)


@app.route('/authorize_discogs',methods=['GET'])
def authorize_discogs():
	
	# oauth 2??
	
	consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
	client = oauth.Client(consumer)
	
	headers = { \
				'User-Agent': user_agent \
				, 'Content-Type' : 'application/x-www-form-urlencoded' \
				, 'oauth_callback' : 'http://bec48fd6.ngrok.io/discogs-ouath2-callback' \
			}
	
	resp, content = client.request(request_token_url, 'POST', headers=headers)
	
	if resp['status'] != '200':
		return ERROR
	
	request_token = dict(urlparse.parse_qsl(content))

	return redirect(''.format(authorize_url, request_token['oauth_token']))
	
	# prepare the client with our API consumer data.
	DISCOGS_CLIENT.set_consumer_key(CONSUMER_KEY, CONSUMER_SECRET)
	token, secret, url = DISCOGS_CLIENT.get_authorize_url(callback_url='http://bec48fd6.ngrok.io/discogs-ouath2-callback')
	

@app.route('/discogs-ouath2-callback',methods=['GET'])
def authorize_discogs(auth_code):
	
	# ouath_verifier is part of the callback url?
	try:
		access_token, access_secret = DISCOGS_CLIENT.get_access_token(auth_code)
	except HTTPError:
		print 'Unable to authenticate.'
		sys.exit(1)
	user = DISCOGS_CLIENT.identity()
	
	for wantlist_item in user.wantlist:
		artists = wantlist_item.release.artists
		labels = wantlist_item.release.labels
		video_urls = [ video.url for video in wantlist_item.release.videos ]