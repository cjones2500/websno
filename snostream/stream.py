'''Data input interface

Data sources run in separate multiprocessing Processes and push their data via
a user-provided callback.
'''

import multiprocessing

class InputStream(multiprocessing.Process):
    '''An objects which receives data and passes it along via a callback'''
    def __init__(self, callback):
        multiprocessing.Process.__init__(self)
        self.callback = callback

    def run(self):
        raise Exception('Cannot call run on InputStream base class')


class EventSource(InputStream):
    '''An InputStream that provides event-level data, for use in an event
    display. Sends Event objects rather than JSON data.'''
    class EventUnavailable(Exception):
        '''Exception raised when an EventSource is unable to provide a requested
        event.
        '''
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr(self.message)


class EventPickleFile(EventSource):
    '''Special event format for websnoed testing'''
    def __init__(self, filename, callback):
        InputStream.__init__(self, callback)

        self.filename = filename

        import pickle
        with open(self.filename) as f:
            self.events = pickle.load(f)

    def run(self):
        '''ship events on a fixed timer'''
        import time
        for ev in self.events:
            self.callback(ev)
            time.sleep(2)

    def get(self, idx):
        '''get an event by index'''
        try:
            return self.events[idx]
        except IndexError:
            raise EventSource.EventUnavailable('Event %i unavailable in %s' % (idx, self.filename))


class RATRootFile(EventSource):
    '''Read events and records from a RAT ROOT file'''
    def __init__(self, filename, callback):
        InputStream.__init__(self, callback)
        from rat import dsreader
        self.dsr = dsreader(filename)


class ZDABFile(EventSource):
    '''Read events and records from a ZDAB file'''
    def __init__(self, filename, callback):
        InputStream.__init__(self, callback)
        import ratzdab
        self.zdabfile = ratzdab.zdabfile(filename)


class ZDABDispatch(EventSource):
    '''Receive events and records from a ZDAB dispatch stream'''
    def __init__(self, hostname, callback):
        InputStream.__init__(self, callback)
        import ratzdab
        self.dispatcher = ratzdab.dispatch(hostname)


class OrcaRootStream(InputStream):
    '''Read and JSONize objects from a normal OrcaRoot stream'''
    def __init__(self, callback):
        InputStream.__init__(self, callback)


class OrcaJSONStream(InputStream):
    '''Read documents from a ZeroMQ OrcaRoot JSON stream'''
    def __init__(self, callback):
        import zmq
        InputStream.__init__(self, callback)


class CouchDBChanges(InputStream):
    '''Read changes from a CouchDB database'''
    def __init__(self, host, dbname, callback, username=None, password=None):
        InputStream.__init__(self, callback)
        import couchdb

        couch = couchdb.Server(host)

        if username and password:
            couch.resource.credentials = (username, password)

        self.db = couch[dbname]

    def run(self):
        for change in self.db.changes(include_docs=True, heartbeat=50000, feed='continuous'):
            doc = change['doc']
            self.callback(doc)

