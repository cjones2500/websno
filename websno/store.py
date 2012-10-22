'''Data storage backends.

These may store data however they like, but present a dict-like interface
to the user.
'''

import bisect

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


class RackStore(DataStore):
    '''Hold per-rack data in memory'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = [{} for i in range(19)]

    def set(self, rack, o):
        for k in o:
            self._store[rack].setdefault(o['key'], []).append([o['timestamp'], o['value']])

    def get(self, rack, key):
        return self._store[rack].get(key, {})


class CrateSlotStore(DataStore):
    '''Hold queues in lists'''
    def __init__(self):
        DataStore.__init__(self)

        self._store = {
            'pmt_base_current': [[{'ts':[0 for x in range(300)], 'v':[{} for x in range(300)]} for sl in range(16)] for cr in range(19)],
            'cmos_rate': [[{'ts':[0 for x in range(300)], 'v':[{} for x in range(300)]} for sl in range(16)] for cr in range(19)],
            'fec_vlt': [[{'ts':[0 for x in range(300)], 'v':[{} for x in range(300)]} for sl in range(16)] for cr in range(19)],
            'xl3_hv': [{'ts':[0 for x in range(3600)], 'v':[{} for x in range(3600)]} for cr in range(19)],
            'xl3_vlt': [{'ts':[0 for x in range(3600)], 'v':[{} for x in range(3600)]} for cr in range(19)],
            'fifo_state': [{'ts':[0 for x in range(3600)], 'v':[{} for x in range(3600)]} for cr in range(19)]
        }

        self.crate_slot = ['pmt_base_current', 'fec_vlt', 'cmos_rate']
        self.crate_only = ['xl3_hv', 'xl3_vlt', 'fifo_state']

    def set(self, l):
        '''Store a list of key/value/timestamp dicts, keep it sorted'''
        for o in l:
            if o['key'] in self.crate_slot:
                slot = self._store['pmt_base_current'][o['crate_num']][o['slot_num']]
                #todo add direction, if we add to past, remove future
                slot['ts'].pop(0)
                slot['v'].pop(0)
                #todo: do not pop, reduce instead into a long term store
                idx_in = bisect.bisect_left(slot['ts'], o['ts'])
                slot['ts'].insert(idx_in, o['ts'])
                slot['v'].insert(idx_in, o['v'])

            elif o['key'] in self.crate_only:
                crate = self._store['xl3_hv'][o['crate_num']]
                crate['ts'].pop(0)
                crate['v'].pop(0)
                idx_in = bisect.bisect_left(crate['ts'], o['ts'])
                crate['ts'].insert(idx_in, o['ts'])
                crate['v'].insert(idx_in, o['v'])

    def get(self, key, dic):
        #todo: redo
        '''Get a list of (timestamp, value) tuples for the requested key over
        the specified time interval (in seconds since epoch).

        :param key: Field (queue) name to look up
        :param interval: tuple -- *optional* (start, end) times to get
        :returns: list of (timestamp, value) tuples
        '''

        crate = dic.get('crate', (0, 18))
        cr_l = range(crate[0], crate[1] + 1)
        slot = dic.get('slot', (0, 15))
        sl_l = range(slot[0], slot[1] + 1)
        interval = dic.get('interval', (1, 3e9))

        l = []
        if key in self.crate_slot:
            for cr in range(19):
                lc = []
                if cr in cr_l:
                    for sl in range(16):
                        ls = []
                        if sl in sl_l:
                            idx_fr = bisect.bisect_left(self._store[key][cr][sl]['ts'], interval[0])
                            idx_to = bisect.bisect_right(self._store[key][cr][sl]['ts'], interval[1], idx_fr)
                            ls.append({
                                'ts': self._store[key][cr][sl]['ts'][idx_fr:idx_to],
                                'v': self._store[key][cr][sl]['v'][idx_fr:idx_to]
                            })
                        lc.append(ls)
                l.append(lc)

        elif key in self.crate_only:
            for cr in range(19):
                lc = []
                if cr in cr_l:
                    idx_fr = bisect.bisect_left(self._store[key][cr]['ts'], interval[0])
                    idx_to = bisect.bisect_right(self._store[key][cr]['ts'], interval[1], idx_fr)
                    lc.append({
                        'ts': self._store[key][cr]['ts'][idx_fr:idx_to],
                        'v': self._store[key][cr]['v'][idx_fr:idx_to]
                    })
                l.append(lc)

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
        raise Exception('CouchBaseStore not implemented')

        DataStore.__init__(self)

        self.host = host
        self.bucket_name = bucket_name

        from couchbase import Couchbase
        self._cb = Couchbase(host, username, password)

        self._bucket = self._cb[bucket_name]

