'''
Data processor for the crate HV status

There is nothing to process here, only basic validation is done

input:
"type": "xl3_hv",
"timestamp": "yyyy-MM-ddTHH:mm:ss.SSSZ" //ORCA
"crate_num": 0, //ORCA
"vlt_a": 0., //V
"vlt_b": 0., //V
"crt_a": 0., //mA
"crt_b": 0. //mA

output:
'key': 'xl3_hv',
'crate_num': 0.,
'ts': 0., //float seconds since epoch
'v': {
    'vlt_a': 0., //V
    'vlt_b': 0., //V
    'crt_a': 0., //mA
    'crt_b': 0. //mA
}
'''

import gevent
import datetime

class HVStatusException(Exception):
    def __init__(self, reason):
        self.reason = reason

class HVStatus(gevent.Greenlet):
    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'timestamp' not in self.o:
            raise HVStatusException('timestamp error')

        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise HVStatusException('crate_num error')

        if 'vlt_a' not in self.o or 0 > self.o['vlt_a'] > 3000:
            raise HVStatusException('vlt_a missing or corrupted')

        if 'vlt_b' not in self.o or 0 > self.o['vlt_b'] > 3000:
            raise HVStatusException('vlt_b missing or corrupted')

        if 'crt_a' not in self.o or 0 > self.o['crt_a'] > 100:
            raise HVStatusException('crt_a missing or corrupted')

        if 'crt_b' not in self.o or 0 > self.o['crt_b'] > 100:
            raise HVStatusException('crt_b missing or corrupted')

    def process(self):
        pass

    def _run(self):
        try:
            self.validate()
        except HVStatusException as e:
            print 'HVStatus packet invalid: ' + e.reason
            return

        #self.process()

        res = []
        ts = float(datetime.datetime.strptime(self.o['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s.%f'))
        res = [{
            'key': self.o['type'],
            'crate_num': self.o['crate_num'],
            'ts': ts,
            'v': {
                'vlt_a': self.o['vlt_a'],
                'vlt_b': self.o['vlt_b'],
                'crt_a': self.o['crt_a'],
                'crt_b': self.o['crt_b']
            }
        }]

        self.rqueue(res)

