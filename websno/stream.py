'''Data input interface

Data sources run in separate threading. Threads and push their data via a
user-provided callback.
'''

import time
import threading
import websno

class InputStream(threading.Thread):
    '''An objects which receives data and passes it along via a callback'''
    def __init__(self):
        threading.Thread.__init__(self)


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
    def __init__(self, filename, interval=2):
        InputStream.__init__(self)

        self.interval = interval
        self.filename = filename
        self.idx = 0

        import pickle
        with open(self.filename) as f:
            self.events = pickle.load(f)

    def run(self):
        '''ship events on a fixed timer'''
        for ev in self.events:
            ev['source'] = 'Event Pickle: %s' % self.filename

            websno.records['event_data'].set(self.iidx, ev)

            self.idx += 1
            time.sleep(self.interval)

    def get(self, idx):
        '''get an event by index'''
        try:
            return self.events[idx]
        except IndexError:
            raise EventSource.EventUnavailable('Event %i unavailable in %s' % (idx, self.filename))


class RATRootFile(EventSource):
    '''Read events and records from a RAT ROOT file'''
    def __init__(self, filename, interval=2):
        InputStream.__init__(self)

        self.filename = filename
        self.interval = interval
        self.idx = 0

        from rat import ROOT
        self.t = ROOT.TChain("T")
        self.t.Add(filename)

        self.ds = ROOT.RAT.DS.Root()
        self.t.SetBranchAddress("ds", self.ds)

    @classmethod
    def ev_to_dict(self, ev, source=''):
        '''convert a RAT::DS::EV to a dictionary websnoed can handle'''
        d = {
            'gtid': hex(ev.GetEventID()),
            'nhit': ev.GetNhits(),
            'trig': ev.GetTrigType(),
            'source': source
        }

        pmtid = []
        qhs = []
        t = []
        for i in range(ev.GetPMTUnCalCount()):
            pmt = ev.GetPMTUnCal(i)
            pmtid.append(pmt.GetID())
            qhs.append(pmt.GetsQHS())
            t.append(pmt.GetsPMTt())

        d['q'] = qhs
        d['t'] = t
        d['id'] = pmtid

        digitizer = ev.GetDigitiser()
        for i in range(digitizer.GetTrigSumCount()):
            waveform = digitizer.GetTrigSum(i).GetSamples()
            d['caen_%i' % i] = []
            for j in range(waveform.size()):
                d['caen_%i' % i].append([j, waveform[j]])

        # try to make histograms with numpy
        try:
            import numpy
            d['qhist'] = map((lambda x: map(float, x)), zip(*reversed(numpy.histogram(d['q'], bins=50))))
            d['thist'] = map((lambda x: map(float, x)), zip(*reversed(numpy.histogram(d['t'], bins=50))))
        except ImportError:
            pass

        return d

    def run(self):
        '''ship events on a fixed timer'''
        for i in range(self.t.GetEntries()):
            self.t.GetEntry(i)

            if not self.ds:
                break

            if self.ds.GetEVCount() > 0:
                d = self.ev_to_dict(self.ds.GetEV(0), 'RAT File: %s' % self.filename)
                websno.records['event_data'].set(i, d)
                self.idx = i

            time.sleep(self.interval)

    def get(self, idx):
        '''get an event by index'''
        if idx > 0 and idx < self.t.GetEntries():
            self.t.GetEntry(idx)
            return self.ev_to_dict(self.ds.GetEV(0))
        else:
            raise EventSource.EventUnavailable('Event %i unavailable in %s' % (idx, self.filename))


class ZDABFile(EventSource):
    '''Read events and records from a ZDAB file'''
    def __init__(self, filename, interval=2):
        InputStream.__init__(self)

        self.filename = filename
        self.interval = interval
        self.idx = 0

        import ratzdab
        self.zdabfile = ratzdab.zdabfile(filename)
        
    def run(self):
        '''ship events on a fixed timer'''
        import ratzdab

        while True:
            try:
                o = self.zdabfile.next()

                if o == None:
                    break

                if o.IsA() == ratzdab.ROOT.RAT.DS.Root.Class():
                    d = RATRootFile.ev_to_dict(o.GetEV(0), 'ZDAB File: %s' % self.filename)
                    websno.records['event_data'].set(o.GetEV(0).GetEventID(), d)
                    self.idx += 1
                    time.sleep(self.interval)

                del o

            except Exception: # fixme: it's a ratzdab::unknown_record_error
                print 'exception: could not unpack record'
                continue


class ZDABDispatch(EventSource):
    '''Receive events and records from a ZDAB dispatch stream'''
    def __init__(self, hostname, interval=1):
        InputStream.__init__(self)

        self.hostname = hostname
        self.interval = interval
        self.previous_event_arrival_time = 0

        import ratzdab
        self.dispatcher = ratzdab.dispatch(hostname)

    def run(self):
        '''ship events as they arrive from the zdab dispatch'''
        import time
        import ratzdab

        while True:
            try:
                o = self.dispatcher.next(False)

                if not o:
                    time.sleep(0.01)
                    continue

                event_arrival_time = time.time()
                if event_arrival_time > previous_event_arrival_time - interval:
                    continue

                if o.IsA() == ratzdab.ROOT.RAT.DS.Root.Class():
                    d = RATRootFile.ev_to_dict(o.GetEV(0), 'ZDAB Dispatch: %s' % self.hostname)
                    websno.records['event_data'].set(o.GetEV(0).GetEventID(), d)

            except Exception: # fixme: it's a ratzdab::unknown_record_error
                continue


class OrcaRootStream(InputStream):
    '''Read and JSONize objects from a normal OrcaRoot stream'''
    def __init__(self):
        raise Exception('OrcaRootStream is not implemented')
        InputStream.__init__(self)


class OrcaJSONStream(InputStream):
    '''Read documents from a ZeroMQ OrcaRoot JSON stream'''
    def __init__(self, address):
        InputStream.__init__(self)

        self.address = address
        from websno.inputstreams import orcajson

        self.orca_json_worker = orcajson.OrcaJSONWorker()
        self.orca_json_worker.start()

    def run(self):
        from zmq import green as zmq

        self._context = zmq.Context() # if multiple zmq streams, move this up

        self._socket = self._context.socket(zmq.SUB)
        self._socket.connect(self.address)
        self._socket.setsockopt(zmq.SUBSCRIBE, '')

        self._ssocket = self._context.socket(zmq.PUSH)
        self._ssocket.connect('ipc:///tmp/snostream_orcajson_input')

        self._rsocket = self._context.socket(zmq.PULL)
        self._rsocket.bind('ipc:///tmp/snostream_orcajson_output')

        poller = zmq.Poller()
        poller.register(self._socket, zmq.POLLIN)
        poller.register(self._rsocket, zmq.POLLIN)

        while True:
            try:
                socks = dict(poller.poll(100))
            except zmq.ZMQError:
                print 'OrcaJSONStream: Poll failed'
                socks = []
                continue

            if self._socket in socks and socks[self._socket] == zmq.POLLIN:
                o = self._socket.recv_json()

                '''
                if o['type'] == 'cmos_rates':
                    if 'timestamp' in o:
                        sample_time = o['timestamp']
                    else:
                        sample_time = time.time()

                    l = []
                    for channel in o['channels']:
                        idx = channel['id']
                        rate = channel['rate']

                        k = '%s_%i' % (o['type'], idx)
                        v = rate

                        l.append({
                            'key': k,
                            'timestamp': sample_time,
                            'value': v
                        })

                    self.callback(l)
                '''

                try:
                    self._ssocket.send_pyobj(o, zmq.NOBLOCK)
                except zmq.ZMQError:
                    #correct way would be to add 1. ssocket into poller as zmq.POLLOUT 2. a queue
                    continue

            if self._rsocket in socks and socks[self._rsocket] == zmq.POLLIN:
                o = self._rsocket.recv_pyobj()
                # FIXME
                #websno.records['event_data'].set(o)

        self.orca_json_worker.join()

class CouchDBChanges(InputStream):
    '''Read changes from a CouchDB database'''
    def __init__(self, host, dbname, username=None, password=None):
        InputStream.__init__(self)
        import couchdb

        couch = couchdb.Server(host)

        if username and password:
            couch.resource.credentials = (username, password)

        self.db = couch[dbname]

    def run(self):
        for change in self.db.changes(include_docs=True, heartbeat=50000, feed='continuous'):
            doc = change['doc']

            if doc['type'] == 'rack_low_voltage':
                websno.records['rack_low_voltage'].set(o)

