import time
import json
from socketio.namespace import BaseNamespace

import snostream

class CMOSRatesNamespace(BaseNamespace):
    _registry = {}

    def on_initialize(self, subscriptions=[]):
        CMOSRatesNamespace._registry[id(self)] = self
        print 'INIT', id(self)

        self.channel = None
        self.last_update = time.time() - 60

    def on_configure(self, settings):
        print 'CONFIGURE', id(self)
        print settings
        self.channel = settings['channel']

    def recv_disconnect(self):
        print 'DISCONNECT', id(self)
        del CMOSRatesNamespace._registry[id(self)]
        self.disconnect(silent=True)

    def recv_message(self, message):
        print "PING!!!", message

    @classmethod
    def update_trigger(self):
        for s in CMOSRatesNamespace._registry.values():
            if not s.channel:
                continue
            interval = (s.last_update, time.time())
            updates = snostream.data_store.get('cmos_rates_%i' % s.channel, interval)
            if len(updates) > 0:
                s.emit('event', json.dumps(updates))
                s.last_update = time.time()

