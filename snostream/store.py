'''Data storage backends.

These may store data however they like, but present a dict-like interface
to the user.
'''

import json
import uuid

class DataStore:
    '''Base class for data storage interfaces'''
    def __init__(self):
        pass


class CouchDBStore(DataStore):
    '''Store queues in a CouchDB database'''
    def __init__(self, host, dbname, username=None, password=None):
        '''Create a CouchDBStore

        :param host: Hostname of CouchDB server
        :param dbname: Name of CouchDB database
        :param username: *optional* CouchDB username
        :param password: *optional* CouchDB password
        '''
        DataStore.__init__(self)

        self.host = host
        self.dbname = dbname

        import couchdb
        self._couch = couchdb.Server(host)

        if username and password:
            self._couch.resource.credentials = (username, password)

        self._db = self._couch[dbname]

    def set(self, key, timestamp, value):
        '''Store a key/value pair with a timestamp
        
        :param key: Field (queue) name
        :param timestamp: float -- time of sample in seconds since epoch
        :param value: Measured value to store
        '''
        d = {
            '_id': uuid.uuid4().hex,
            'key': key,
            'timestamp': timestamp,
            'value': value
        }

        self._db.save(d)

    def get(self, key, interval=None):
        '''Get a list of (timestamp, value) tuples for the requested key over
        the specified time interval (in seconds since epoch).

        :param key: Field (queue) name to look up
        :param interval: tuple -- *optional* (start, end) times to get
        :returns: list -- list of (timestamp, value) tuples
        '''
        if interval:
            kwargs = {'startkey': [key,interval[0]], 'endkey': [key,interval[1]]}
        else:
            kwargs = {'startkey': [key], 'endkey': [key,{}]}

        l = []
        for row in self._db.view('foo/asdf', **kwargs):
            l.append((row.key[1], row.value))

        return l

class CouchBaseStore(DataStore):
    '''Store queues in a CouchBase DB'''
    def __init__(self, host, username, password, bucket_name='default'):
        DataStore.__init__(self)

        self.host = host
        self.bucket_name = bucket_name

        from couchbase import Couchbase
        self._cb = Couchbase(host, username, password)

        self._bucket = self._cb[bucket_name]


class MemoryStore(DataStore):
    '''Hold queues in memory'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = {}

