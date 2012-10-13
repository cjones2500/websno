import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

public_files = []
for root, dirs, files in os.walk('websno/public'):
    for name in files:
        public_files.append(os.path.join(root, name).split(os.sep, 1)[-1])

setup(
    name = "websno",
    version = "0.1",
    author = "atm rvb jk",
    author_email = "amastbaum@gmail.com",
    description = ("sno+ detector monitoring"),
    license = "BSD",
    url = "http://github.com/mastbaum/websno",
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: BSD License",
    ],
    packages = ['websno', 'websno.apps', 'websno.inputstreams', 'websno.inputstreams.orcajson'],
    package_data = {'websno': public_files},
    scripts = ['bin/websno', 'bin/websnoed'],
    install_requires = ['gevent-socketio'],
    zip_safe = False
)

