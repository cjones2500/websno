'''
Data processor for XL3 voltages

There is nothing to process here, only basic validation is done

input:
"type": "xl3_vlt",
"timestamp": "yyyy-MM-ddTHH:mm:ss.SSSZ" //ORCA
"crate_num": 0, //ORCA
"VCC": 0.,
"VEE": 0.,
"VP24": 0.,
"VM24": 0.,
"TMP0": 0.,
"TMP1": 0.,
"TMP2": 0.

output:
'key': 'xl3_hv',
'crate_num': 0.,
'ts': 0., //float seconds since epoch
'v': {
    'VCC': 0.,
    'VEE': 0.,
    'VP24': 0.,
    'VM24': 0.,
    'TMP0': 0.,
    'TMP1': 0.,
    'TMP2': 0.
}
'''

import gevent
import datetime

class XL3VoltagesException(Exception):
    def __init__(self, reason):
        self.reason = reason

class XL3Voltages(gevent.Greenlet):
    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'timestamp' not in self.o:
            raise XL3VoltagesException('timestamp error')

        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise XL3VoltagesException('crate_num error')

        if 'VCC' not in self.o or -100 > self.o['VCC'] > 100:
            raise XL3VoltagesException('VCC missing or corrupted')

        if 'VEE' not in self.o or -100 > self.o['VEE'] > 100:
            raise XL3VoltagesException('VEE missing or corrupted')

        if 'VP24' not in self.o or -100 > self.o['VP24'] > 100:
            raise XL3VoltagesException('VP24 missing or corrupted')

        if 'VM24' not in self.o or -100 > self.o['VM24'] > 100:
            raise XL3VoltagesException('VM24 missing or corrupted')

        if 'TMP0' not in self.o or -100 > self.o['TMP0'] > 100:
            raise XL3VoltagesException('TMP0 missing or corrupted')

        if 'TMP1' not in self.o or -100 > self.o['TMP1'] > 100:
            raise XL3VoltagesException('TMP1 missing or corrupted')

        if 'TMP2' not in self.o or -100 > self.o['TMP2'] > 100:
            raise XL3VoltagesException('TMP2 missing or corrupted')

    def process(self):
        pass

    def _run(self):
        try:
            self.validate()
        except XL3VoltagesException as e:
            print 'XL3Voltages packet invalid: ' + e.reason
            return

        #self.process()

        ts = float(datetime.datetime.strptime(self.o['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s.%f'))
        res = [{
            'key': self.o['type'],
            'crate_num': self.o['crate_num'],
            'ts': ts,
            'v': {
                'VCC': self.o['VCC'],
                'VEE': self.o['VEE'],
                'VP24': self.o['VP24'],
                'VM24': self.o['VM24'],
                'TMP0': self.o['TMP0'],
                'TMP1': self.o['TMP1'],
                'TMP2': self.o['TMP2']
            }
        }]

        self.rqueue(res)

