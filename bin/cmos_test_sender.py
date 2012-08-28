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
    
    for i in range(random.randrange(200, 300)):
        d['channels'].append({
            'id': random.randrange(0, 9728),
            'rate': max(0, random.normalvariate(1000, 1000))
        })

    socket.send_json(d)

    reply = socket.recv_json()

    if reply['ok'] == True:
        print 'ACK'

    time.sleep(1)

