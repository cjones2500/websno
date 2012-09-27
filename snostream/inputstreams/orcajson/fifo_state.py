'''
Data processor for FIFO state packets.

These are pushed into ORCA by XL3 PING command. Timestamps are added.

input:
"type": "fifo_state",
"crate_num": 0,
"fifo": [ 0.0, ... ], //16 slots
"XL3_buffer": 0.0,

output:
'key': 'fifo_state',
'crate_num': 0.,
'ts': 0., //float seconds since epoch
'v': {
    'fifo': [0., ...],
    'XL3_buffer': 0.
}
'''

import gevent
import time

class FifoStateException(Exception):
    def __init__(self, reason):
        self.reason = reason

class FifoState(gevent.Greenlet):
    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise FifoStateException('crate_num error')

        if 'fifo' not in self.o or type(self.o['fifo']) is not list or len(self.o['fifo']) != 16:
            raise FifoStateException('fifo data error')

        for fifo in self.o['fifo']:
            if 0 > fifo > 100:
                raise FifoStateException('fifo state corrupted')

        if 'XL3_buffer' not in self.o or 0 > self.o['XL3_buffer'] > 100:
            raise FifoStateException('XL3 buffer error')

    def process(self):
        pass

    def _run(self):
        try:
            self.validate()
        except FifoStateException as e:
            print 'FifoState packet invalid: ' + e.reason
            return

        #self.process()

        ts = time.time()
        res = [{
            'key': self.o['type'],
            'crate_num': self.o['crate_num'],
            'ts': ts,
            'v': {
                'fifo': self.o['fifo'],
                'XL3_buffer': self.o['XL3_buffer']
            }
        }]

        self.rqueue(res)

