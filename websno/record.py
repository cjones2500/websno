'''Data interchange classes'''

class Record:
    '''A piece of information to be used in websno.'''
    def __init__(self, name, stream, store=None):
        self.name = name
        self.stream = stream
        self.store = store
        self.subscribers = {}

    def subscribe(self, namespace, callback, filt=None):
        '''Subscribe namespace to changes in this record, filtered by callable
        filt.
        '''
        self.subscribers[namespace] = {
            'filter': filt,
            'callback': callback
        }
        print 'record', self.name, 'registered subscriber', namespace

    def unsubscribe(self, namespace):
        '''Unsubscribe a namespace from changes.'''
        del self.subscribers[namespace]

    def get(self, *kwargs):
        '''Get a value from the store.'''
        return self.store.get(*kwargs)

    def set(self, *kwargs):
        '''Set a value in the appropriate store and send it to subscribed
        namespaces.
        '''
        if self.store is not None:
            self.store.set(*kwargs)

        # send data to subscribed namespaces
        for namespace, o in self.subscribers.items():
            if o['filter'] is not None and not o['filter'](*kwargs):
                continue
            o['callback'](*kwargs)

