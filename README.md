WebSNO
=========
*real-time monitoring for ALL the things*

Installation
------------
    $ python setup.py install

`setup.py` will install `gevent-socketio`, the only required dependency for websno. Optional features have additional requirements:

* `numpy` is needed for creating event charge and time histograms
* `pyzmq-static` is needed for listening to Orca JSON streams
* `couchdb` is needed for listening to CouchDB changes feeds and for certain storage backends.

Usage
-----
For testing, snostream will read events from a file:

    $ ./bin/websno file.root # or .zdab, or .pickle, or ZDAB dispatcher hostname

Configuration
-------------
Better configuration is planned, too, but for now, hack `bin/websno`. Register `Records` to bind data sources to storage and client subscriptions.
