import os

from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer

from websno.apps.websnoed import websnoed
from websno.apps.cmostest import cmos

base_path = os.path.abspath(os.path.dirname(__file__))

app_paths = ['websnoed', 'cmos']

class Application(object):
    def __init__(self):
        self.buffer = []
        self.request = {'_': []}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>THE INDEX PAGE!</h1>']

        serve = False
        if path.startswith('static/'):
            path = os.path.join(base_path, path)
            serve = True
        else:
            for app_path in app_paths:
                if path.startswith(app_path):
                    app_path_slash = app_path + '/'
                    path = os.path.join(base_path,'apps',app_path,'public',path.replace(app_path_slash,'',1))
                    serve = True
                    break

        if serve:
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
            routes = {
                '/websnoed': websnoed.EventViewerNamespace,
                '/cmos': cmos.CMOSRatesNamespace
            }
            socketio_manage(environ, routes, self.request)
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

