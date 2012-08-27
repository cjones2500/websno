import os

from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer

import apps.websnoed

base_path = os.path.abspath(os.path.dirname(__file__))

app_paths = ['websnoed.html']

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

        if path.startswith('static/') or path in app_paths:
            if path in app_paths:
                path = os.path.join(base_path, 'apps', path)
            else:
                path = os.path.join(base_path, path)

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
            # socketio namespaces here
            socketio_manage(environ, {'': apps.websnoed.EventViewerNamespace}, self.request)
        else:
            return not_found(start_response)

def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']

def serve():
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()

