'''
Data processor for XL3 voltages

There is nothing to process here, only basic validation is done.
The voltage are: -24V Sup, -15V Sup, VEE, -3.3V Sup, -2.0V Sup,
3.3V Sup, 4.0V Sup, VCC, 6.5V Sup, 8.0V Sup, 15V Sup, 24V Sup,
-2.0V Ref, -1.0V Ref, 0.8V Ref, 1.0V Ref, 4.0V Ref, 5.0V Ref,
Temp in deg C, Cal DAC, HV current in mA.

input:
"type": "fec_vlt",
"timestamp": "yyyy-MM-ddTHH:mm:ss.SSSZ" //ORCA
"crate_num": 0, //ORCA
"slot_num": 0, //ORCA
"voltage": [ 0., ... ] // 21 float voltages

output:
'key': 'xl3_hv',
'crate_num': 0.,
'slot_num': 0.,
'ts': 0., //float seconds since epoch
'v': {
    'voltage': [0., ...]
}
'''

import gevent
import datetime

class FECVoltagesException(Exception):
    def __init__(self, reason):
        self.reason = reason

class FECVoltages(gevent.Greenlet):
    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'timestamp' not in self.o:
            raise FECVoltagesException('timestamp error')

        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise FECVoltagesException('crate_num error')

        if 'slot_num' not in self.o or not 0 <= self.o['crate_num'] <= 15:
            raise FECVoltagesException('slot_num error')

        if 'voltage' not in self.o or type(self.o['voltage']) is not list or len(self.o['voltage']) != 21:
            raise FECVoltagesException('voltage error')

        for vlt in self.o['voltage']:
            if vlt -100 > vlt > 100:
                raise FECVoltagesException('voltage corrupted')

    def process(self):
        pass

    def _run(self):
        try:
            self.validate()
        except FECVoltagesException as e:
            print 'FECVoltages packet invalid: ' + e.reason
            return

        #self.process()

        ts = float(datetime.datetime.strptime(self.o['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s.%f'))
        res = [{
            'key': self.o['type'],
            'crate_num': self.o['crate_num'],
            'slot_num': self.o['slot_num'],
            'ts': ts,
            'v': {
                'voltage': self.o['voltage']
            }
        }]

        self.rqueue(res)

