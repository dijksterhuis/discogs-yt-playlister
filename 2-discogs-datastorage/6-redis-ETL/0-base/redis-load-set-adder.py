#!/usr/local/bin/python
import json, argparse, redis, os, pymongo, time
from sys import stdout as console
from sys import exit
from datetime import datetime as dt

"""
ETL Script for insert daa into Redis instances for the Discogs Youtube Playlister
- Take discogs data (r_key/r_value) from various Mongo DB instances (masters, releases)
- Insert to Redis in specified format (sorted_set, meta_unique_filt, autocomplete)
- Use --verbose argument to print more detailed info to stdout
"""

class MyLogger:
    
    """ Logger class to write inserts to disk, along with any other important information.
    """
    
    def __init__(self, headers = None, path='/logging/tmp'):
        self.path = path + dt.now().strftime('__%Y%m%d_%Hh%Mm%Ss') + '.txt'
        self.headers = headers
        self.data = None
        self.log_count = 0
        if isinstance(self.headers, list): self.write_log_data(headers)
    
    def _exception_printing(print_string, error):
        print(print_string+'. Exception: ',e)
    
    def write_log_data(self, data):
        if isinstance(data,list): log_data = ','.join(list(map(str, data)))
        else: log_data = str(data)
        try:
            with open(self.path,'a+') as log_f:
                log_f.write(log_data + '\n')
        except IOError as e:
            self._exception_printing('Could not read/write log file: '+log_file, e)
        except ValueError as e:
            self._exception_printing('Data of the wrong type.', e)
        except Exception as e:
            self._exception_printing('An exception occured.', e)
        else:
            self.log_count += 1
            
    def get_log_count(self):
        return self.log_count

def print_verbose(string):
    """
    Print the string if verbosity (argparse arg) is true
    """
    if verbose_bool is True:
        if type(string) is list: print(*string)
        else: print(string)

def recursive_gen(in_json,tag,rec_counter):
    
    """
    Recursively look for and yield tags from Mongo documents
    @src, genre, style, year, artist_id etc.
    """
    # -- we've gone down one level of nesting / recursion
    
    rec_counter += 1
    
    # -- we found the item(s) we're looking for!
    
    if type(in_json) is dict and tag in in_json.keys(): yield in_json[tag]
        
    # -- else then we're at the bottom of the json object, skip
    
    elif type(in_json) is str: pass
    
    # if list, we need to iterate over the list elements and redo recursion
    
    elif type(in_json) is list:
        for list_item in in_json:
            for value in recursive_gen(list_item,tag,rec_counter): yield value
    
    # -- no found key, another level we can go to
    
    elif type(in_json) is dict:
        for key in in_json:
            for value in recursive_gen(in_json[key],tag,rec_counter): yield value
                
    # ---- nothing found, ignore
    
    else: pass

def get_values(metadata_tags,document):
    
    for tag in metadata_tags:
        val = [value for value in recursive_gen(document,tag,0)]
        if len(val) > 1: yield (tag, val)
        elif len(val) == 0: yield (tag, None)
        else: yield (tag,val[0])

def mongo_connect(mongo_conn_host):
    
    """
    Connect to Mongo instance
    """
    
    print_verbose( 'Setting up Mongo DB connection to: '+ mongo_conn_host )
    mongo_conn_dict = { 'host' : 'mongo-discogs-' + mongo_conn_host, 'port' : 27017, 'db' : 'discogs', 'coll' : mongo_conn_host }
    
    m = pymongo.MongoClient(mongo_conn_dict['host'],mongo_conn_dict['port'])
    db = m[mongo_conn_dict['db']]
    print_verbose('Mongo connection ping result: {}'.format(db.command('ping')))
    c = db[mongo_conn_dict['coll']]
    print_verbose('{:,d} Mongo documents'.format(c.count()))
    
    if c.count() == 0:
        print('No data in Mongo instance '+mongo_conn_host+'. Exiting.')
        exit(0)
    
    return c

def redis_connect(redis_conn_host):
    
    """
    Connect to Redis instance
    """
    
    print_verbose( 'Setting up Redis Connection to: ' + redis_conn_host )
    redis_conn = redis.Redis( host=redis_conn_host, port=6379 )
    outputs = [ redis_conn ]
    
    ping_result = redis_conn.ping()
    print_verbose( 'Redis connection ping result: {}'.format(ping_result) )
    
    if ping_result is False:
        print('COULD NOT CONNECT TO '+redis_conn_host+'. EXITING.')
        exit(500)
    
    init_redis_dbsize = redis_conn.dbsize()
    
    print_verbose('Currently '+str(init_redis_dbsize)+' keys in '+redis_conn_host)
    
    print_verbose('Setting up Redis Pipeline.')
    
    return redis_conn, redis_conn.pipeline(), init_redis_dbsize

def primary_key_list_check_gen(i,j):
    """ If data is type(list), output each item as str """
    if isinstance(i,list) and isinstance(j,list):
        for k_1 in i:
            for k_2 in j: yield str(k_1), str(k_2)
    elif isinstance(i,list):
        for k in i: yield str(k), str(j)
    elif isinstance(i,list):
        for k in j: yield str(i), str(k)
    else: yield str(i), str(j)

def set_redis_insert(redis_conn, logs, key, value):
    """ Insert data into redis set instance 
    - TODO Not happy about logs being here - needs too many variables...
    """
    try: counter = redis_conn.sadd( key, value )
    except Exception as e:
        print('--- An exception occured.',e)
        logs.write_log_data([key, value, False , "Error: " +str(e)])
        counter = 0
    else: logs.write_log_data([key, value, True , False])
    return counter

def sorted_set_redis_insert(redis_conn, logs, key, value, idx):
    """ Insert data into redis sorted set instance 
    - TODO Not happy about logs being here - needs too many variables...
    """
    v = value.upper() + ':' + value
    if redis_conn.zscore( key, v ) is None:
        try: counter = redis_conn.zadd( key, v, 0)
        except Exception as e:
            print('--- An exception occured.',e)
            logs.write_log_data([idx, key, v, False , "Error: " +str(e)])
            counter = 0
        else: logs.write_log_data([idx, key, v, True , False])
    else:
        # --- TODO increment frequency of key
        counter = 0
        logs.write_log_data([key, v, False , True])
    return counter


def main(args):
    
    """
    1. Open a redis connection
    2. Open a mongo connection
    3. Iterate over mongo dox
    4. Get the required bits from mongo
    5. Insert into redis
    6. Stats print out
    """
    
    run_type, primary_key_check, redis_conn_host, mongo_conn_host, r_key, r_value = \
             args.run_type[0]\
             , args.primary_key[0]\
             , args.redis_insert_host[0]\
             , args.mongo_connection_host[0]\
             , args.redis_key[0]\
             , args.redis_value[0]
    
    print('Setting up logger.')
    headers = ['mongo_idx','r_key','r_val','inserted','skipped']
    
    logs = MyLogger( path = '/logging/redis_inserts__' + redis_conn_host, headers = headers)
    
    print('\nSetting up database connections.')
    
    redis_conn, r_pipeline, init_redis_dbsize = redis_connect(redis_conn_host)
    mongo_conn = mongo_connect(mongo_conn_host)
    
    print('DB connections set up, beginning data extraction...\n')
    
    dataset, total_dox, starttime, counter = mongo_conn.find(), mongo_conn.count(), dt.now(), 0
    
    for idx, document in enumerate( dataset ):
        
        # ---- get the relevant data from document
        
        metadata_tags = [ r_key, r_value ]
        inserts = { key: value for key, value in get_values( metadata_tags,document ) }
        
        # ---- set up key, value pairs
        
        if run_type == 'simple': key, value = inserts[r_key], inserts[r_value]
        elif run_type == 'autocomplete': key, value = r_value, inserts[r_value]
        
        # ---- iterate over all elements if any are lists
        
        for k, v in primary_key_list_check_gen(key, value):
            
            # ---- if no (useful) data, log and do nothing
            
            if k is None or v is None: 
                logs.write_log_data([idx, key, value, False , True])
                
            elif key.isalnum() is False or value.isalnum() is False:
                logs.write_log_data([idx, key, value, False , True])
            
            # ---- else do inserts
            
            elif run_type == "simple": counter += set_redis_insert(redis_conn, logs, k, v, idx)
            elif run_type == 'autocomplete': counter += sorted_set_redis_insert(redis_conn, logs, k, v, idx)
            
            # ---- what other conditions are there?!
            
            else: pass
        
        # ---- stats
        
        console.write( "\r{:,d} proc / {:,d} mongo dox".format( idx, total_dox ))
        console.flush()
    
    # ---- execute redis pipeline
    
    print_verbose('Executing redis pipeline.')
    r_pipeline.execute()
    
    mongo_conn.close()
    
    # ---- print stats
    
    elapsed_time, redis_additions = dt.now() - starttime, redis_conn.dbsize() - init_redis_dbsize
    print('\nExtraction complete!')
    print_verbose( '{:,d} keys were actually added to the {:s} Redis DB'.format(redis_additions, redis_conn_host) )
    print_verbose( 'Redis counter is at: {:,d}. Does this match?'.format(counter) )
    print_verbose( 'Time taken (mins): {:,f}'.format(elapsed_time.total_seconds()//60) )

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="REDIS SET INSERTS: Get data from Mongo and load into Redis")
    
    parser.add_argument('run_type',type=str,nargs=1,choices=['simple','autocomplete'])
    parser.add_argument('primary_key',type=str,nargs=1,choices=['key','value'])
    parser.add_argument('mongo_connection_host',type=str,nargs=1,choices=['masters','labels','releases','artists'])
    parser.add_argument('redis_insert_host',type=str,nargs=1)
    parser.add_argument('redis_key',type=str,nargs=1)
    parser.add_argument('redis_value',type=str,nargs=1)
    parser.add_argument('--verbose','-v',action='store_true')
    
    args = parser.parse_args()
    
    global verbose_bool
    verbose_bool = args.verbose
    
    main(args)