import json
from socketio.namespace import BaseNamespace

import websno

class EventViewerNamespace(BaseNamespace):
    event_getter = None

    def on_initialize(self, subscriptions=[]):
        self.settings = {
            'nhit_threshold': 0,
            'trigger_type': 0xffffffff
        }
        self.user_control = False
        self.event_index = 0
        websno.records['event_data'].subscribe(self, self.emit_event, self.filter_event)
        print 'INIT', id(self)

    def on_control_back(self):
        print 'BACK'
        try:
            ev = json.dumps(self.event_getter(self.event_index - 1))
            self.event_index -= 1
            self.user_control = True
            self.emit('event', ev)
        except Exception:
            self.emit('alarm', "Can't get previous event")

    def on_control_forward(self):
        print 'FORWARD'
        try:
            ev = json.dumps(self.event_getter(self.event_index + 1))
            self.event_index += 1
            self.user_control = True
            self.emit('event', ev)
        except Exception:
            self.emit('alarm', "Can't get next event")

    def on_control_toggle_pause(self):
        self.user_control = not self.user_control

    def on_configure(self, settings):
        print 'CONFIGURE', id(self)
        self.settings['nhit_threshold'] = int(settings['nhit_threshold'] or 0)
        self.settings['trigger_type'] = int(settings['trigger_type'] or 0xffffffff)

    def recv_disconnect(self):
        print 'DISCONNECT', id(self)
        websno.records['event_data'].unsubscribe(self)
        self.disconnect(silent=True)

    def recv_message(self, message):
        print "PING!!!", message

    def filter_event(self, i, ev):
        return ev['nhit'] >= self.settings['nhit_threshold'] and (ev['trig'] & self.settings['trigger_type'])

    def emit_event(self, i, ev):
        '''send an event to the client'''
        self.emit('event', json.dumps(ev))

