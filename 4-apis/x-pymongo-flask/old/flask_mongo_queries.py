#!flask/bin/python
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
import json, os, datetime, time, pymongo, werkzeug, requests, flask

# TODO - pip install flask-httpauth

"""
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""


app = Flask(__name__)
auth = HTTPBasicAuth()
mongodb = pymongo.MongoClient('mongo-discogs',27017)['discogs']


@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/am_i_alive', methods=['GET'])
def check_if_alive():
	return jsonify({'status': 'yes! I am!' })

@app.route('/masters', methods=['POST'])
#@auth.login_required
def masters():
	if not request.json:
		abort(400)
	else:		
		query_dict = json.loads(request.json)
		collection = mongodb['masters']
		search = collection.find(query_dict)
		print(search)
		for result in search:
			print(result)
			yield jsonify(result), 201

@app.route('/artists-query', methods=['POST'])
#@auth.login_required
def run_query():
	if not request.json:
		abort(400)
	else:		
		# TODO
		print('no data yet!')	
		return jsonify({'url' : 'No data yet!' , 'title' : 'no data yet!' }), 201


if __name__ == '__main__':
	app.run(debug=True)

