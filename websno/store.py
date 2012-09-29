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


class MemoryStore(DataStore):
    '''Hold queues in memory'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = {}

    def set(self, l):
        '''Store a list of key/value/timestamp dicts'''
        for o in l:
            self._store.setdefault(o['key'], []).append([o['timestamp'], o['value']])

    def get(self, key, interval=None):
        '''Get a list of (timestamp, value) tuples for the requested key over
        the specified time interval (in seconds since epoch).

        :param key: Field (queue) name to look up
        :param interval: tuple -- *optional* (start, end) times to get
        :returns: list of (timestamp, value) tuples
        '''
        l = self._store.get(key, [])

        # this is really inefficient. use a b-tree orsomething.
        if interval:
            l = filter(lambda x: x[0]>interval[0] and x[0]<interval[1], l)

        return l


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

    def set(self, l):
        '''Store a list of key/value/timestamp dicts'''
        self._db.update(l)

    def get(self, key, interval=None):
        '''Get a list of (timestamp, value) tuples for the requested key over
        the specified time interval (in seconds since epoch).

        :param key: Field (queue) name to look up
        :param interval: tuple -- *optional* (start, end) times to get
        :returns: list of (timestamp, value) tuples
        '''
        if interval:
            kwargs = {'startkey': [key,interval[0]], 'endkey': [key,interval[1]]}
        else:
            kwargs = {'startkey': [key], 'endkey': [key,{}]}

        l = [(r.key[1], r.value) for r in self._db.view('foo/asdf', **kwargs)]

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

