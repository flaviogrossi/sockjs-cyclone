import sys

import cyclone

from twisted.internet import reactor
from twisted.python import log

from sockjs.cyclone.conn import SockJSConnection, MultiplexConnection
from sockjs.cyclone.router import SockJSRouter


class IndexHandler(cyclone.web.RequestHandler):
    """ Serve the chat html page """
    def get(self):
        self.render('index.html')


class AnnConnection(SockJSConnection):
    def connectionMade(self, info):
        self.sendMessage('Ann says hi!!')

    def messageReceived(self, message):
        self.sendMessage('Ann nods: ' + message)


class BobConnection(SockJSConnection):
    def connectionMade(self, info):
        self.sendMessage('Bob doesn\'t agree.')

    def messageReceived(self, message):
        self.sendMessage('Bob says no to: ' + message)


class CarlConnection(SockJSConnection):
    def connectionMade(self, info):
        self.sendMessage('Carl says goodbye!')
        self.close()

    def messageReceived(self, message):
        pass


if __name__ == "__main__":
    def main():
        multiplexConnection = MultiplexConnection.create(ann=AnnConnection,
                                                         bob=BobConnection,
                                                         carl=CarlConnection)

        echoRouter = SockJSRouter(multiplexConnection, '/echo')

        app = cyclone.web.Application(
                      [ (r'/', IndexHandler) ] + echoRouter.urls )
        reactor.listenTCP(8888, app)
        reactor.run()

    log.startLogging(sys.stdout)
    main()

