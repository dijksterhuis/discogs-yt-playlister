#!flask/bin/python
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, abort, Resource, Api
import json, os, datetime, time, pymongo, werkzeug, requests, flask

"""
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
"""

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

mongodb = pymongo.MongoClient('mongo-discogs-artists-api-service',27017)['discogs']
collection = mongodb['artists']

#parser = reqparse.RequestParser()
#parser.add_argument('json',action='append',type=str,required=True,help="provide a valid JSON input",location=('jsons','values'))

def remove_objectid_gen(dictionary,keys_to_ignore):
	"""
	DEPRECIATED - removing the keys to ignore bit (handled in the mongo query as projections)
	Do the dictionary part of the below in a generator expression:
	- { key : value for key, value in search_result.items() if key != '_id' } for search_result in search
	"""
	if type(keys_to_ignore) in [list,str,tuple,set]:
		for key, value in dictionary.items():
			if key in keys_to_ignore and type(keys_to_ignore) in [list,tuple,set] \
			or key == keys_to_ignore and type(keys_to_ignore) is str:
				# - if in the keys_to_ignore (set/tuple,list) 
				# - or equals a specified str value
				# - then ignore it!
				pass
			else:
				# - otherwise, return the key and value(s)
				yield (key , value)
	else:
		return (None, None)

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class am_i_alive(Resource):
    def get(self):
        return {'status': 'OK'}

class artists(Resource):
	def post(self):
		
		# - get request - be nice if reqparse could be used for this...
		
		ping_result = mongodb.command('ping')
		print('mongo connection ping result: ', ping_result)
		
		query_dict = request.get_json()
		print('query: ',query_dict)

		# - Handling nested requests.... Is this needed?
		# - Probably, I'm lazy and the fullstops mess with code conventions
		# '{"aliases.name":"Dick Track"}' vs. '{"aliases" : {"name":"Dick Track"}}'
		
		for top_key,top_value in query_dict.items():
			if type(top_value) is dict:
				for sub_key,sub_values in top_value.items():
					string_replace = str(key) + '.' + str(sub_key)
					if string_replace not in query_dict.keys():
						query_dict[string_replace] = [query_dict.pop(top_key)]
					# - what if I want to search for multiples?
					# - !!! this is the mongodb rest api, not the redis one - hold your horses you madman!
					#else:
					#	query_dict[string_replace].append( query_dict.pop(top_key) )
			else:
				pass			

		print('formatted query: ',query_dict)
		
		fields_to_ignore = {'_id':False , 'images' : False}
		
		search = collection.find( query_dict , projection=fields_to_ignore )
		
		# - Generate results out of the mongo.find search object (execute the search in a list(dict()) comprehension...)

		results = [ { key : value for key, value in search_result } for search_result in search ]
		
		##### DEPRECIATED VERISONS OF LIST COMP
		
		# 1. - ignore fields once back on server, can use projections with mongodb, so one that instead (less data transfer)
		#ign = ('_id','images')
		#results = [ { key : value for key, value in remove_objectid_gen(search_result,ign) } for search_result in search ]

		# 2. - https://stackoverflow.com/a/41010331
		#results = [ { key : value for key, value in search_result.items() if key != '_id' } for search_result in search ]
		
		print('results: ',results)
		print('numb results: ',len(results))
		
		# - misc handling of output data (cleaning up)
		
		if len(results) is 1:
			return results[0],201
		elif len(results) is 0:
			return "No data found for your query: "+json.dumps(query_dict), 400
		else:
			return results, 201

api.add_resource(am_i_alive ,'/am_i_alive')
api.add_resource(artists, '/artists')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=False)
	#app.run(debug=True,port=80)