import elasticsearch
import logging
import json
import redis

# Open connections
rc = redis.Redis(decode_responses=True)
es = elasticsearch.Elasticsearch()

def init_elasticsearch():
    """ Create the ElasticSearch index. """
    mappings = {
        "properties": {
            "name": { "type": "text" },
            "age": { "type": "integer" }
        }
    }
    es.indices.delete(index='idx', ignore=[400, 404])
    es.indices.create(index='idx', mappings=mappings)


def init_redis():
    """ Intialize Redis. """
    rc.flushall()


def init():
    """ Check environment. """
    if not rc.ping():
        logging.error('Redis is not available')
        exit(1)
    if not es.ping():
        logging.error('ElasticSearch is not available')
        exit(1)
    logging.info('Environment is ready.')

    # Initialize Redis
    init_redis()

    # Initialize ElasticSearch
    init_elasticsearch()


def load_data():
    """ Load data to Redis. """
    users = [
        {
            'id': 1,
            'name': 'Rick Sanchez',
            'age': 74
        },
        {
            'id': 2,
            'name': 'Morty Smith',
            'age': 14
        }
    ]
    
    for user in users:
        key = f'user:{user["id"]}'
        rc.json().set(key, '$', user)
        try:
            es.index(index='idx', id=key, document=user)
        except Exception as e:
            # Failed to sync with ElasticSearch - TODO.
            pass

def do_query():
    """ Execute the query in ElasticSearch. """
    query = {
        "bool": {
            "must": {
                "range": {
                    "age": {
                        "gt": 50
                    }
                }
            }
        }
    }
    return es.search(index='idx', query=query)

if __name__ == '__main__':
    init()
    load_data()
    result = do_query()
    print(result)