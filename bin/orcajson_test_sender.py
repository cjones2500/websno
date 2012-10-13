'''Sends fake orca json packets for testing'''

import gevent
from zmq import green as zmq
import random
import datetime

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
            'adc': [[128 + int(click % 50) for j in range(32)] for i in range(16)],
            'busy_flag': [[0 for j in range(32)] for i in range(16)]
        }
        d['adc'][4][3] = 128
        d['adc'][4][7] = 126
        d['busy_flag'][4][11] = 1
        d['busy_flag'][4][16] = 7
        click = (click + 1) % 50

        socket.send_json(d)
        gevent.sleep(polling_delay)

def hv_status():
    vlt = 0;
    while True:
        d = {
            'type': 'xl3_hv',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'crate_num': 12,
            'vlt_a': vlt,
            'vlt_b': max(0, vlt - 20 - random.normalvariate(10,10)),
            'crt_a': vlt * 40.0 / 1000.0,
            'crt_b': max(0, vlt * 35.0 / 1000.0 - random.normalvariate(3,3))
        }
        vlt = (vlt + 10) % 1800 
        socket.send_json(d)
        gevent.sleep(polling_delay)

def xl3_voltages():
    trend = 0;
    while True:
        d = {
            'type': 'xl3_vlt',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'crate_num': 12,
            'VCC': 4.85 + trend * 0.4 + random.normalvariate(0, 0.1),
            'VEE': -12.05 + trend * 0.5 + random.normalvariate(0, 0.3),
            'VP24': -23.7 - trend * 0.7 + random.normalvariate(0, 0.4),
            'VM24': 24.6 - trend * 0.9 + random.normalvariate(0, 0.4),
            'TMP0': 1.9 + trend * 0.05 + random.normalvariate(0, 0.01),
            'TMP1': 1.85 + trend * 0.04 + random.normalvariate(0, 0.01),
            'TMP2': 2.03 - trend * 0.01 + random.normalvariate(0, 0.01)
        }
        trend = (trend + 0.01) % 1.
        socket.send_json(d)
        gevent.sleep(polling_delay)

def fec_voltages():
    trend = 0;
    while True:
        for slot in range(16):
            d = {
                'type': 'fec_vlt',
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'crate_num': 12,
                'slot_num': slot,
                'voltage': [
                    -23.7 - trend * 0.7 + random.normalvariate(0, 0.4),
                    -15.3 + trend * 0.5 + random.normalvariate(0, 0.3),
                    -11.7 + trend * 0.4 + random.normalvariate(0, 0.3),
                    -3.2 - trend * 0.2 + random.normalvariate(0, 0.2),
                    -2.2 + trend * 0.3 + random.normalvariate(0, 0.1),
                    3.1 + trend * 0.1 + random.normalvariate(0, 0.1),
                    4.2 - trend * 0.2 + random.normalvariate(0, 0.2),
                    4.9 + trend * 0.1 + random.normalvariate(0, 0.2),
                    6.3 + trend * 0.4 + random.normalvariate(0, 0.3),
                    8.0 + trend * 0.0 + random.normalvariate(0, 0.3),
                    15.2 - trend * 0.5 + random.normalvariate(0, 0.3),
                    24.0 + trend * 0.3 + random.normalvariate(0, 0.4),
                    -2.2 + trend * 0.3 + random.normalvariate(0, 0.1),
                    -1.1 + trend * 0.1 + random.normalvariate(0, 0.1),
                    0.8 - trend * 0.1 + random.normalvariate(0, 0.1),
                    1.1 - trend * 0.3 + random.normalvariate(0, 0.1),
                    4.2 - trend * 0.2 + random.normalvariate(0, 0.2),
                    4.9 + trend * 0.1 + random.normalvariate(0, 0.2),
                    28.0 + trend * 5 + random.normalvariate(0, 0.3),
                    10.0 + trend * 0 + random.normalvariate(0, 0.1),
                    0.0 + trend * 0.1 + random.normalvariate(0, 0.1)
                ]
            }
            socket.send_json(d)

        trend = (trend + 0.01) % 1.
        gevent.sleep(polling_delay)

def fifo_state():
    trend = 0;
    while True:
        d = {
            'type': 'fifo_state',
            'crate_num': 12,
            'fifo': [min(100, i + trend * (45 + i) / 60 + random.normalvariate(0, 5)) for i in range(16)],
            'XL3_buffer': min(100, 10 + trend + random.normalvariate(0, 5))
        }

        trend = (trend + 1) % 110
        socket.send_json(d)
        gevent.sleep(polling_delay)


def cmos_count():
    count = [[0 for ch in range(32)] for sl in range(16)]
    while True:
        count = [[int(ch + max(0, random.normalvariate(4000, 2000))) % 0x80000000 for ch in sl] for sl in count]

        dl = {
            'type': 'cmos_counts',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'crate_num': 12,
            'slot_mask': 0x00ff,
            'channel_mask': [0xffffffff for i in range(16)],
            'error_flags': 0x00,
            'count': count[0:8]
        }
        socket.send_json(dl)

        dh = {
            'type': 'cmos_counts',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'crate_num': 12,
            'slot_mask': 0xcf00,
            'channel_mask': [0xffffffff for i in range(16)],
            'error_flags': 0x02,
            'count': count[8:12] + count[14:16] + [[0 for ch in range(16)] for sl in range(2)]
        }
        socket.send_json(dh)
        gevent.sleep(polling_delay)


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:5028')
polling_delay = 1.0

gevent.joinall([
    gevent.spawn(pmt_base_current),
    gevent.spawn(hv_status),
    gevent.spawn(xl3_voltages),
    gevent.spawn(fec_voltages),
    gevent.spawn(fifo_state),
    gevent.spawn(cmos_count)
])


