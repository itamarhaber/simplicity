import logging
import redis

# Open connections
rc = redis.Redis(decode_responses=True)

def init_redis():
    """ Initialize Redis and create the index. """
    from redis.commands.search.field import NumericField, TextField
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType
    SCHEMA = (
        TextField("$.name", sortable=True, as_name="name"),
        NumericField("$.age", sortable=True, as_name="age"),
    )
    definition = IndexDefinition(index_type=IndexType.JSON)
    try:
        rc.ft('idx').dropindex(delete_documents=True)
    except redis.exceptions.ResponseError as e:
        if e == 'Unknown Index name':
            pass
    rc.flushall()
    rc.ft('idx').create_index(SCHEMA, definition=definition)


def init():
    """ Check environment. """
    if not rc.ping():
        logging.error('Redis is not available')
        exit(1)

    # Initialize Redis
    init_redis()


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


def do_query():
    """ Execute the query in Redis. """
    return rc.ft('idx').search('@age:[50 +inf]')


if __name__ == '__main__':
    init()
    load_data()
    result = do_query()
    print(result)