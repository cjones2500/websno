'''Data storage backends.

These may store data however they like, but present a dict-like interface
to the user.
'''

import json
import uuid

from snostream.apps.cmos import CMOSRatesNamespace

def run_async(func):
    '''Run a function in a Thread

    Source:
      http://code.activestate.com/recipes/576684-simple-threading-decorator/
    '''
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func


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

    def set(self, l):
        '''Store a list of key/value/timestamp dicts'''
        self._db.update(l)
        CMOSRatesNamespace.update_trigger()

    #@run_async
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


class MemoryStore(DataStore):
    '''Hold queues in memory'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = {}

