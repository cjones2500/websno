'''Sends fake CMOS rates for testing'''

import zmq
import random
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.bind('tcp://*:5028')

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

    reply = socket.recv_json()

    if not reply or 'ok' not in reply:
        print 'communication error'
        break

    print 'send'
    #time.sleep(0.02)

