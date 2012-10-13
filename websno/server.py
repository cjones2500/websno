import os

from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer

from websno.apps import websnoed

base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'public')

class Application(object):
    def __init__(self):
        self.buffer = []
        self.request = {'_': []}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path.endswith("/"):
          path += 'index.html'
        path = path.strip('/')

        print path
        print base_path

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>THE INDEX PAGE!</h1>']


        if path.startswith("socket.io"):
            routes = {
                '/websnoed': websnoed.EventViewerNamespace,
            }
            socketio_manage(environ, routes, self.request)
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

def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']

def serve():
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()

