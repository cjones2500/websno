import gevent
import datetime

class PmtBaseCurrentException(Exception):
    def __init__(self, reason):
        self.reason = reason

class PmtBaseCurrent(gevent.Greenlet):
    def __init__(self, o, rqueue):
        self.o = o
        self.rqueue = rqueue
        gevent.Greenlet.__init__(self)

    def validate(self):
        if 'timestamp' not in self.o:
            raise PmtBaseCurrentException('timestamp error')

        if 'crate_num' not in self.o or not 0 <= self.o['crate_num'] <= 19:
            raise PmtBaseCurrentException('crate_num error')

        if 'slot_mask' not in self.o or self.o['slot_mask'] > 0xffff:
            raise PmtBaseCurrentException('slot mask error')

        if 'channel_mask' not in self.o or type(self.o['channel_mask']) is not list or len(self.o['channel_mask']) != 16:
            raise PmtBaseCurrentException('channel mask error')

        if 'error_flags' not in self.o:
            raise PmtBaseCurrentException('error_flags missing')

        if 'adc' not in self.o:
            raise PmtBaseCurrentException('adc error')

    def process(self):
        self.o['adc'] = [map(lambda x: x - 127, slot) for slot in self.o['adc']]

    def _run(self):
        try:
            self.validate()
        except PmtBaseCurrentException as e:
            print 'PmtBaseCurrent packet invalid: ' + e.reason
            return

        self.process()

        res = []
        ts = datetime.datetime.strptime(self.o['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s.%f'),
        for s_idx, slot in enumerate(self.o['adc']):
            if self.o['slot_mask'] >> s_idx & 0x1 == 0: continue
            for ch_idx, channel in enumerate(slot):
                if self.o['channel_mask'][s_idx] >> ch_idx & 0x1 == 0: continue
                res.append({
                    'key': '%s_%d_%d_%d' % (self.o['type'], self.o['crate_num'], s_idx, ch_idx),
                    'timestamp': ts,
                    'value': channel
                })

        self.rqueue(res)

