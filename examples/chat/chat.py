import sys

import cyclone

from twisted.internet import reactor
from twisted.python import log

import sockjs.cyclone


class IndexHandler(cyclone.web.RequestHandler):
    """ Serve the chat html page """
    def get(self):
        self.render('index.html')


class ChatConnection(sockjs.cyclone.SockJSConnection):
    """ Chat sockjs connection """
    participants = set()

    def connectionMade(self, info):
        self.broadcast(self.participants, "Someone joined.")
        self.participants.add(self)

    def messageReceived(self, message):
        self.broadcast(self.participants, message)

    def connectionLost(self):
        self.participants.remove(self)
        self.broadcast(self.participants, "Someone left.")


if __name__ == "__main__":
    def main():
        ChatRouter = sockjs.cyclone.SockJSRouter(ChatConnection, '/chat')

        app = cyclone.web.Application( [ (r"/", IndexHandler) ] +
                                       ChatRouter.urls )
        reactor.listenTCP(8888, app)
        reactor.run()

    log.startLogging(sys.stdout)
    main()
