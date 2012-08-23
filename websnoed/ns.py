from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace

class EventViewerNamespace(BaseNamespace):
    _registry = {}
    def on_initialize(self, subscriptions=[]):
        self._registry[id(self)] = self
        self.subscriptions = subscriptions

    def recv_disconnect(self):
        del EventViewerNamespace._registry[id(self)]
        self.disconnect(silent=True)

    def recv_message(self, message):
        print "PING!!!", message

    @staticmethod
    def broadcast(event, msg):
        for s in EventViewerNamespace._registry.values():
            # check subs
            s.emit(event, msg)

# data source
import time
import threading
import pickle
import json
with open('events.pickle') as f:
    events = pickle.load(f)
def event_reader():
    for ev in events:
        EventViewerNamespace.broadcast('event', json.dumps(ev))
        time.sleep(2)

t = threading.Thread(target=event_reader)
t.start()

class Application(object):
    def __init__(self):
        self.buffer = []
        self.request = {'_': []}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>Welcome. '
                'Try the <a href="/index.html">chat</a> example.</h1>']

        if path.startswith('static/') or path == 'index.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'': EventViewerNamespace}, self.request)
        else:
            return not_found(start_response)

def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']

if __name__ == '__main__':
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()

