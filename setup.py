import os
import tarfile
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "snostream",
    version = "0.1",
    author = "atm rvb jk fd",
    author_email = "amastbaum@gmail.com",
    description = ("sno+ detector monitoring"),
    license = "BSD",
    url = "http://github.com/mastbaum/derp-octo-hipster",
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: BSD License",
    ],
    packages = ['snostream'],
    scripts = ['bin/snostream'],
    install_requires = ['gevent-socketio'],
)

