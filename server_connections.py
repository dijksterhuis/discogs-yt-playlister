import redis
from pymongo import MongoClient
metadata_redis = redis.Redis(host='redis-metadata-master-ids',port='6379')
jsons_mongo = MongoClient('discogs-mongo',27017)