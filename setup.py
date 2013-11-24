#!/usr/bin/env python

from distutils.core import setup


def readfile(fname):
    with open(fname) as f:
        content = f.read()
    return content


setup(name='sockjs-cyclone',
      version='1.0.2',
      author='Flavio Grossi',
      author_email='flaviogrossi@gmail.com',
      description='SockJS python server for the Cyclone Web Server',
      license=readfile('LICENSE'),
      long_description=readfile('README.rst'),
      keywords=[ 'sockjs',
                 'cyclone',
                 'web server',
                 'websocket'
               ],
      url='http://github.com/flaviogrossi/sockjs-cyclone/',
      packages=[ 'sockjs',
                 'sockjs.cyclone',
                 'sockjs.cyclone.transports'
               ],
      requires=[ 'twisted (>=12.0)',
                 'cyclone (>=1.0)',
                 'simplejson'
               ],
      install_requires=[ 'twisted>=12.0',
                         'cyclone>=1.0-rc8',
                         'simplejson'
                       ],
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Framework :: Twisted',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
          'Topic :: Software Development :: Libraries :: Python Modules',
      )
)
