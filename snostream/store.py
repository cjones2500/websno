'''Data storage backend'''

class DataStore:
    pass

class CouchBase(DataStore):
    '''Store queues in a CouchBase DB'''
    pass

class MemoryStore(DataStore):
    '''Hold queues in memory'''
    pass

