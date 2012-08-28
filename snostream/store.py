'''Data storage backends.

These may store data however they like, but present a dict-like interface
to the user.
'''

import json

class DataStore:
    '''Base class for data storage interfaces'''
    def __init__(self):
        pass

class CouchBase(DataStore):
    '''Store queues in a CouchBase DB'''
    def __init__(self, username, password, bucket_name='default'):
        DataStore.__init__(self)

        self.host = host
        self.bucket_name = bucket_name

        from couchbase import Couchbase
        self._cb = Couchbase(host, username, password)

        self._bucket = self._cb[bucket_name]

    def set(self, key, timestamp, value):
        print 'SET', key, timestamp, value

    def __setitem__(self, key, value):
        try:
            self._bucket[key] = value
        except TypeError:
            # convert to a json string
            # raises TypeError if value can't be serialized
            s = json.dumps(value)
            self._bucket[key] = s

    def __getitem__(self, key):
        return json.loads(self._bucket[key])

class MemoryStore(DataStore):
    '''Hold queues in memory'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = {}

    def set(self, key, timestamp, value):
        print 'SET', key, timestamp, value

    def __setitem__(self, key, value):
        self._store[key] = value

    def __getitem__(self, key):
        return self._store[key]

