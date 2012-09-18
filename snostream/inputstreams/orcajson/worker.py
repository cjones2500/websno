'''ORCA JSON worker

Separate process to crunch the ZeroMQ ORCA JSON stream. Each packet type is processed
in a dedicated greelet pool. The pool is the tool to control resources, and spawns
a greenlet for each packet. Gevent queues are used to distribute packets to pools,
and collect the processed results. A ZeroMQ ipc socket returns the processed packet
to stream.py as a ready-to-store list of dictionaries.
'''

import multiprocessing
import gevent
import gevent.pool
from zmq import green as zmq

class ProcessorPool(object):
    def __init__(self, num, proc, rqueue):
        self.pool = gevent.pool.Pool(num)
        self.proc = proc
        self.rqueue = rqueue

    def add_job(self, o):
        if not self.pool.full():
            self.pool.start(self.proc(o, self.rqueue))

    def terminate(self):
        self.pool.kill()


class _OrcaJSONWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True

    def respond(self):
        self._rsocket = self._context.socket(zmq.PUSH)
        self._rsocket.connect('ipc:///tmp/snostream_orcajson_output')

        self.running = True
        while self.running:
            o = self.rqueue.get()
            self._rsocket.send_pyobj(o, zmq.NOBLOCK)

    def run(self):
        from snostream.inputstreams import orcajson
        self._context = zmq.Context()
        self._ssocket = self._context.socket(zmq.PULL)
        self._ssocket.bind('ipc:///tmp/snostream_orcajson_input')

        self.rqueue = gevent.queue.Queue()
        gevent.spawn(self.respond)

        poller = zmq.Poller()
        poller.register(self._ssocket, zmq.POLLIN)

        pmt_base_current_pool = ProcessorPool(20, orcajson.PmtBaseCurrent, self.rqueue.put)

        while True:
            socks = dict(poller.poll(10)) 
            if self._ssocket in socks and socks[self._ssocket] == zmq.POLLIN:
                o = self._ssocket.recv_pyobj()
                if o['type'] == 'pmt_base_current':
                    pmt_base_current_pool.add_job(o)

