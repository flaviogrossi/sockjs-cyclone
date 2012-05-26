import sys
import math

from twisted.python import log
from twisted.internet import reactor, task

from cyclone import web

from sockjs.cyclone import SockJSConnection
from sockjs.cyclone import SockJSRouter


class EchoConnection(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)


class CloseConnection(SockJSConnection):
    def on_open(self, info):
        self.close()

    def on_message(self, msg):
        pass


class TickerConnection(SockJSConnection):
    def on_open(self, info):
        self.timeout = task.LoopingCall(self._ticker)
        self.timeout.start(1)

    def on_close(self):
        self.timeout.stop()

    def _ticker(self):
        self.send('tick!')


class BroadcastConnection(SockJSConnection):
    clients = set()

    def on_open(self, info):
        self.clients.add(self)

    def on_message(self, msg):
        self.broadcast(self.clients, msg)

    def on_close(self):
        self.clients.remove(self)


class AmplifyConnection(SockJSConnection):
    def on_message(self, msg):
        n = int(msg)
        if n < 0 or n > 19:
            n = 1

        self.send('x' * int(math.pow(2, n)))


class CookieEcho(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)


class SockJsTestServer(web.Application, object):
    def __init__(self):
        settings = dict(autoescape=None)

        echoRouter = SockJSRouter(EchoConnection, '/echo',
                        user_settings=dict(response_limit=4096))
        wsOffRouter = SockJSRouter(EchoConnection, '/disabled_websocket_echo',
                        user_settings=dict(disabled_transports=['websocket']))
        closeRouter = SockJSRouter(CloseConnection, '/close')
        tickerRouter = SockJSRouter(TickerConnection, '/ticker')
        amplifyRouter = SockJSRouter(AmplifyConnection, '/amplify')
        broadcastRouter = SockJSRouter(BroadcastConnection, '/broadcast')
        cookieRouter = SockJSRouter(CookieEcho, '/cookie_needed_echo')

        handlers = (echoRouter.urls + wsOffRouter.urls + closeRouter.urls +
                    tickerRouter.urls + amplifyRouter.urls +
                    broadcastRouter.urls + cookieRouter.urls)

        super(SockJsTestServer, self).__init__(handlers, **settings)


if __name__ == '__main__':
    def main():
        reactor.listenTCP(8081, SockJsTestServer())
        reactor.run()

    log.startLogging(sys.stdout)
    main()

