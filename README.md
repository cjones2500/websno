snostream
=========
*real-time monitoring for ALL the things*

Installation
------------
    $ python setup.py install

Usage
-----
For testing, snostream will read events from a file:

    $ ./bin/snostream file.root # or .zdab, or .pickle

It can also read events from a ZDAB dispatch stream. More (non-event level) data sources are forthcoming.

Configuration
-------------
Better configuration is planned, too, but for now, hack `bin/snostream`. Instantiate data sources and give them a callback -- they call this callable with data received.