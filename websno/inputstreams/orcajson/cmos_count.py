'''
Data processor for the CMOS count packets.

CMOS counts are processed into rates. The input packet contains up to 8 slots.
The counts are stored in the class (static) array. This runs in multiple greenlets,
so clashes are likely. Practically it doesn't matter, we get the correct rates.

input:
"type": "cmos_counts",
"timestamp": "yyyy-MM-ddTHH:mm:ss.SSSZ" //ORCA
"crate_num": 0, //ORCA
"slot_mask": 0xffff,
"channel_mask": [ 0xffffffff, ..., 0xffffffff ], //all 16 slots
"error_flags": 0x0000,
"counts": [ [ 0*0, ..., 0*31], ..., [ 7*0, ..., 7*31 ] ] //8 slots * 32 channels

output:
'key': 'cmos_rate',
'crate_num': cr,
'slot_num': slot,
'ts': ts,
'vl': {
    'channel_mask': 0xffffffff,
    'rate': [0,...]
}

'''

import gevent
import datetime

class CmosCountException(Exception):
    def __init__(self, reason):
        self.reason = reason

class CmosCount(gevent.Greenlet):
    dat = [[[{'cnt': 0, 'ts': 0} for ch in range(32)] for sl in range(16)] for cr in range(19)]
    max_time = 10 # do not calculate rates from counts if the time between counts is more than

    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        self.d = []
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'timestamp' not in self.o:
            raise CmosCountException('timestamp error')

        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise CmosCountException('crate_num error')

        if 'slot_mask' not in self.o or self.o['slot_mask'] > 0xffff:
            raise CmosCountException('slot mask error')

        if 'channel_mask' not in self.o or type(self.o['channel_mask']) is not list or len(self.o['channel_mask']) != 16:
            raise CmosCountException('channel mask error')

        if 'error_flags' not in self.o:
            raise CmosCountException('error_flags missing')

        if 'count' not in self.o:
            raise CmosCountException('adc missing')

    def process(self):
        ts = float(datetime.datetime.strptime(self.o['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s.%f'))
        slots = self.o['slot_mask']
        sl_cnt = 0
        cr = self.o['crate_num']
        for slot in range(16):
            if self.o['slot_mask'] >> slot & 0x1:
                if not self.o['error_flags'] >> slot & 0x1:
                    ch_mask = self.o['channel_mask'][slot]
                    sl_channel_mask = 0
                    sl_rates = []
                    for ch in range(32):
                        #bit 31 in cmos counts means busy
                        rate = 0
                        if ch_mask >> ch & 0x1 and not self.o['count'][sl_cnt][ch] >> 31 & 0x1:
                            if 0 < ts - CmosCount.dat[cr][slot][ch]['ts'] < CmosCount.max_time:
                                rate = self.o['count'][sl_cnt][ch] & 0x7fffffff - CmosCount.dat[cr][slot][ch]['cnt']
                                if rate < 0: rate += 0x80000000
                                rate /= ts - CmosCount.dat[cr][slot][ch]['ts']
                                sl_channel_mask |= 1 << ch

                            CmosCount.dat[cr][slot][ch]['cnt'] = self.o['count'][sl_cnt][ch] & 0x7fffffff
                            CmosCount.dat[cr][slot][ch]['ts'] = ts

                        sl_rates.append(rate)

                    if sl_channel_mask:
                        self.d.append({
                            'key': 'cmos_rate',
                            'crate_num': cr,
                            'slot_num': slot,
                            'ts': ts,
                            'v': {
                                'channel_mask': sl_channel_mask,
                                'rate': list(sl_rates)
                            }
                        })

                #increment even if the error flag is set
                sl_cnt += 1

    def _run(self):
        try:
            self.validate()
        except CmosCountException as e:
            print 'CmosCount packet invalid: ' + e.reason
            return

        self.process()

        self.rqueue(self.d)

