'''Sends fake orca json packets for testing'''

import gevent
from zmq import green as zmq
import random
import datetime

def cmos_rate_andy():
    while True:
        d = {
            'type': 'cmos_rates',
            'channels': []
        }
        
        for i in range(32):
            d['channels'].append({
                'id': i,
                'rate': max(0, random.normalvariate(1000, 1000))
            })

        socket.send_json(d)
        gevent.sleep(polling_delay / 2.)

def pmt_base_current():
    click = 0
    while True:
        d = {
            'type': 'pmt_base_current',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'crate_num': 12,
            'slot_mask': 0xf37f,
            'channel_mask': [0xffffffff for i in range(16)],
            'error_flags': 0x0000,
            'adc': [[128 + int(click % 50) for j in range(32)] for i in range(16)]
        }
        d['adc'][4][3] = 128
        d['adc'][4][7] = 126
        click = (click + 1) % 50

        socket.send_json(d)
        gevent.sleep(polling_delay)


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:5028')
polling_delay = 1.

gevent.joinall([
    gevent.spawn(cmos_rate_andy),
    gevent.spawn(pmt_base_current),
])


