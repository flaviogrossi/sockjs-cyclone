#!/usr/bin/env python

from distutils.core import setup


def readfile(fname):
    with open(fname) as f:
        content = f.read()
    return content


setup(name='sockjs-cyclone',
      version='0.0.1',
      author='Flavio Grossi',
      author_email='flaviogrossi@gmail.com',
      description='SockJS python server for the Cyclone Web Server',
      license=readfile('LICENSE'),
      long_description=readfile('README.rst'),
      url='http://github.com/mrjoes/sockjs-tornado/',
      packages=[ 'sockjs', 'sockjs.cyclone', 'sockjs.cyclone.transports' ],
      requires=[ 'cyclone', 'twisted (>=12.0)', 'simplejson' ],
      classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Framework :: Twisted',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
          'Topic :: Software Development :: Libraries :: Python Modules',
      )
)
