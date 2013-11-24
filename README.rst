.. contents:: Table of contents


SockJS-cyclone
==============

.. image:: https://badge.fury.io/py/sockjs-cyclone.png
    :target: https://pypi.python.org/pypi/sockjs-cyclone

.. image:: https://secure.travis-ci.org/flaviogrossi/sockjs-cyclone.png?branch=master
   :target: http://travis-ci.org/#!/flaviogrossi/sockjs-cyclone

.. image:: https://pypip.in/d/sockjs-cyclone/badge.png
   :target: https://crate.io/packages/sockjs-cyclone/

SockJS-cyclone is a pure Python server implementation for the
`SockJS client library <https://github.com/sockjs/sockjs-client>`_
running on the `Cyclone <http://cyclone.io>`_ web server.

SockJS-cyclone is released under the `MIT license
<https://github.com/flaviogrossi/sockjs-cyclone/tree/master/LICENSE>`_.

What is SockJS?
---------------

`SockJS <http://sockjs.org>`_ is a browser JavaScript library that provides a
WebSocket-like object.  SockJS gives you a coherent, cross-browser, JavaScript
API which creates a low latency, full duplex, cross-domain communication
channel between the browser and the web server, which consistently works across
old browsers, misconfigured or old proxies and firewalls, etc. by automatically
using other transports as a fallback mechanism.

SockJS main features:

- simple APIs, as close to the WebSocket API as possible;
- scaling and load balancing techniques;
- very fast connection establishment;
- pure JavaScript library on the client-side, no flash needed;
- very extensive code testing available for both the server and client sides.

SockJS-cyclone fully supports the SockJS protocol version 0.3.3.

What is Cyclone?
----------------

`Cyclone <http://cyclone.io>`_ is a very fast and scalable web server framework
that implements the Tornado API as a Twisted protocol.

How does it look like?
----------------------

A live demo deployed on Heroku can be found `here <http://sockjs-cyclone-demo.herokuapp.com>`_.

Here is a small example for an echo server:

.. code-block:: python

    from twisted.internet import reactor
    import cyclone
    import sockjs.cyclone

    class EchoConnection(sockjs.cyclone.SockJSConnection):
        def messageReceived(self, message):
            self.sendMessage(message)

    if __name__ == "__main__":
        EchoRouter = sockjs.cyclone.SockJSRouter(EchoConnection, '/echo')
        app = cyclone.web.Application(EchoRouter.urls)
        reactor.listenTCP(8888, app)
        reactor.run()

and an excerpt for the client:

.. code-block:: javascript

    var sock = new SockJS('http://mydomain.com/echo');
    sock.onopen = function() {
        console.log('open');
    };
    sock.onmessage = function(e) {
        console.log('message', e.data);
    };
    sock.onclose = function() {
        console.log('close');
    };
    sock.send('hello!');

Complete examples `can be found here <https://github.com/flaviogrossi/sockjs-cyclone/tree/master/examples>`_.

Multiplexing
------------

SockJS-Cyclone supports multiplexing (multiple distinct channels over a single
shared connection):

.. code-block:: python

    from twisted.internet import reactor
    import cyclone
    from sockjs.cyclone.conn import SockJSConnection, MultiplexConnection
    from sockjs.cyclone.router import SockJSRouter

    class AnnConnection(SockJSConnection):
        def messageReceived(self, message):
            self.sendMessage('Ann received ' + message)

    class BobConnection(SockJSConnection):
        def messageReceived(self, message):
            self.sendMessage('Bob received ' + message)

    class CarlConnection(SockJSConnection):
        def messageReceived(self, message):
            self.sendMessage('Carl received ' + message)

    if __name__ == "__main__":
        multiplexConnection = MultiplexConnection.create(ann=AnnConnection,
                                                         bob=BobConnection,
                                                         carl=CarlConnection)

        echoRouter = SockJSRouter(multiplexConnection, '/echo')

        app = cyclone.web.Application(echoRouter.urls)
        reactor.listenTCP(8888, app)
        reactor.run()

See the `websocket-multiplex <https://github.com/sockjs/websocket-multiplex>`_
library for the client support, and the `complete example 
<https://github.com/flaviogrossi/sockjs-cyclone/tree/master/examples/multiplex>`_.


Installation
============

Install from pypi with:

::

    pip install sockjs-cyclone

or from the latest sources with:

::

    git clone https://github.com/flaviogrossi/sockjs-cyclone.git
    cd sockjs-cyclone
    python setup.py install


SockJS-cyclone API
==================

The main interaction with SockJS-cyclone happens via the two classes
``SockJSRouter`` and ``SockJSConnection``.

SockJSConnection
----------------

The ``SockJSConnection`` class represent a connection with a client and
contains the logic of your application. Its main methods are:

- ``connectionMade(request)``: called when the connection with the client is
  established;
- ``messageReceived(message)``: called when a new message is received from the
  client;
- ``sendMessage(message)``: call when you want to send a new message to the
  client;
- ``close()``: close the connection;
- ``connectionLost()``: called when the connection with the client is lost or
  explicitly closed.

SockJSRouter
------------

The ``SockJSRouter`` class routes the requests to the various connections
according to the url prefix. Its main methods are:

- ``__init__(connection, prefix, user_settings)``: bounds the given connection
  to the given url prefix;
- ``urls``: read only property to be used to initialize the cyclone application
  with all the needed sockjs urls.


Deployment
==========

SockJS servers are usually deployed in production behind reverse proxies and/or
load balancers. The most used options are currently `Nginx <http://nginx.org>`_
and `HAProxy <http://haproxy.1wt.eu>`_.

For Heroku deployment, see the `quickstart instructions here <https://github.com/flaviogrossi/sockjs-cyclone_heroku_quickstart>`_.

Nginx
-----

Two major options are needed to fully support proxying requests to a
SockJS-Cyclone server: setting the HTTP protocol version to 1.1 and `passing
upgrade headers to the server <http://nginx.org/en/docs/http/websocket.html>`_.
The relevant portion of the required configuration is:

::

    server {
        listen       80;
        server_name  localhost;

        location / {
            proxy_pass          http://<sockjs_server>:<port>;
            proxy_http_version  1.1;
            proxy_set_header    Upgrade $http_upgrade;
            proxy_set_header    Connection "upgrade";
            proxy_set_header    Host $http_host;
            proxy_set_header    X-Real-IP $remote_addr;
        }

    }

For websocket support, nginx version 1.3.13 or above is needed.

A working ``nginx.conf`` example can be found `in the examples directory <https://github.com/flaviogrossi/sockjs-cyclone/tree/master/examples/deployment>`_.

HAProxy
-------

A complete example for HAProxy deployment and load balancing can be found on
``SockJS-Node`` `Readme <https://github.com/sockjs/sockjs-node#deployment-and-load-balancing>`_.


Credits
=======

Thanks to:

- Serge S. Koval for the tornado implementation;
- VoiSmart s.r.l for sponsoring the project.
