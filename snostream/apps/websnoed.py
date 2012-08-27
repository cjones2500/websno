import json

from gevent import monkey
monkey.patch_all()

from socketio.namespace import BaseNamespace

from snostream import registry

class EventViewerNamespace(BaseNamespace):
    _registry = {}

    def on_initialize(self, subscriptions=[]):
        self.settings = {
            'nhit_threshold': 0,
            'trigger_type': 0xffffffff
        }
        self.user_control = False
        self.event_index = 0
        EventViewerNamespace._registry[id(self)] = self
        print 'INIT', id(self)

    def on_control_back(self):
        print 'BACK'
        try:
            ev = json.dumps(source.get_event(self.event_index - 1))
            self.event_index -= 1
            self.user_control = True
            self.emit('event', ev)
        except IndexError:
            self.emit('alarm', "Can't get previous event")

    def on_control_forward(self):
        print 'FORWARD'
        try:
            ev = json.dumps(get_event(self.event_index + 1))
            self.event_index += 1
            self.user_control = True
            self.emit('event', ev)
        except IndexError:
            self.emit('alarm', "Can't get next event")

    def on_control_toggle_pause(self):
        self.user_control = not self.user_control

    def on_configure(self, settings):
        print 'CONFIGURE', id(self)
        self.settings['nhit_threshold'] = int(settings['nhit_threshold'] or 0)
        self.settings['trigger_type'] = int(settings['trigger_type'] or 0xffffffff)

    def recv_disconnect(self):
        print 'DISCONNECT', id(self)
        del EventViewerNamespace._registry[id(self)]
        self.disconnect(silent=True)

    def recv_message(self, message):
        print "PING!!!", message

    @classmethod
    def broadcast_event(self, idx, ev):
        for s in filter(lambda x: not x.user_control, EventViewerNamespace._registry.values()):
            print ev['nhit']
            if not ev['nhit'] >= s.settings['nhit_threshold']:
                continue

            if not (ev['trig'] & s.settings['trigger_type']):
                continue

            s.event_index = idx
            s.emit('event', json.dumps(ev))

