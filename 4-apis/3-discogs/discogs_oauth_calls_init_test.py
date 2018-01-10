import sys, discogs_client
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import json, os, datetime, time, requests
from random import randint

# https://github.com/jesseward/discogs-oauth-example/blob/master/discogs_client_example.py
# https://www.discogs.com/applications/edit/16092

CONSUMER_KEY = 'JPrYAjenmsVzglNdpuxG'
CONSUMER_SECRET = 'ZiXHVuuuaitcIvsCxuUaOkFFTdmaeTjx'
REQUEST_TOKEN_URL =	'https://api.discogs.com/oauth/request_token'
AUTHORIZE_URL = 'https://www.discogs.com/oauth/authorize'
ACCESS_TOKEN_URL= 'https://api.discogs.com/oauth/access_token'

USER_AGENT = 'discogs-yt-playlister/1.0'
DISCOGS_CLIENT = discogs_client.Client(user_agent)

@app.route('/authorize_discogs',methods=['GET'])
def authorize_discogs():
	
	# instantiate our discogs_client object.

	
	# prepare the client with our API consumer data.
	DISCOGS_CLIENT.set_consumer_key(CONSUMER_KEY, CONSUMER_SECRET)
	token, secret, url = DISCOGS_CLIENT.get_authorize_url()
	
	return redirect(url)

@app.route('/discogs-ouath2-callback',methods=['GET'])
def authorize_discogs():
	
	# ouath_verifier is part of the callback url?
	try:
		access_token, access_secret = DISCOGS_CLIENT.get_access_token(oauth_verifier)
	except HTTPError:
		print 'Unable to authenticate.'
		sys.exit(1)
	user = discogsclient.identity()
	wantlist = user['username'].wantlist
	
	
	content, resp = discogsclient._fetcher.fetch(None, 'GET', list, headers={'User-agent': DISCOGS_CLIENT.user_agent})
	discogsclient/users/{username}/lists