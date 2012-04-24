import sys

from twisted.python import log
from twisted.internet import reactor

from cyclone import web

from sockjs.cyclone import SockJsConnection
from sockjs.cyclone import SockJsRouter


class EchoConnection(SockJsConnection):
    def on_message(self, msg):
        self.send(msg)


class SockJsTestServer(web.Application, object):
    def __init__(self):
        settings = dict(autoescape=None)

        echoRouter = SockJsRouter(EchoConnection, prefix='/echo')

        handlers = echoRouter.urls

        for spec in handlers:
            print '----------------------'
            print spec
            print '----------------------'


        print '-----------------------------'
        print echoRouter.urls
        print '-----------------------------'

        super(SockJsTestServer, self).__init__(handlers, **settings)


if __name__ == '__main__':
    def main():
        reactor.listenTCP(8081, SockJsTestServer())
        reactor.run()

    log.startLogging(sys.stdout)
    main()

